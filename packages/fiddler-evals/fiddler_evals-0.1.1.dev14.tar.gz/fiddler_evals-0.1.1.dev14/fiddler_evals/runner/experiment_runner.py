from __future__ import annotations

import inspect
import logging
import signal
import time
from collections import OrderedDict
from dataclasses import dataclass
from functools import cached_property, wraps
from typing import Any, Callable, Dict

from tqdm.autonotebook import tqdm

from fiddler_evals.connection import get_connection
from fiddler_evals.entities.dataset import Dataset
from fiddler_evals.entities.experiment import (
    Experiment,
    ExperimentItemStatus,
    ExperimentStatus,
)
from fiddler_evals.evaluators.base import (
    ALLOWED_PARAM_KINDS,
    Evaluator,
    ScoreFnKwargsMappingType,
)
from fiddler_evals.evaluators.eval_fn import EvalFn
from fiddler_evals.exceptions import ScoreFunctionInvalidArgs, TaskFunctionInvalidArgs
from fiddler_evals.libs.http_client import RequestClient
from fiddler_evals.pydantic_models.dataset import DatasetItem
from fiddler_evals.pydantic_models.error import get_error_from_exception
from fiddler_evals.pydantic_models.experiment import (
    ExperimentItemResult,
    NewExperimentItem,
)
from fiddler_evals.pydantic_models.score import Score, ScoreStatus
from fiddler_evals.runner.experiment_result_publisher import ExperimentResultPublisher
from fiddler_evals.utils.tqdm import thread_map

logger = logging.getLogger(__name__)

# Function(inputs, extras, metadata) -> outputs
EvalTaskType = Callable[
    [Dict[str, Any], Dict[str, Any], Dict[str, Any]], Dict[str, Any]
]


@dataclass
class ExperimentResult:
    """Result of evaluating a complete experiment."""

    experiment: Experiment
    results: list[ExperimentItemResult]


def with_signal_handlers(func: Callable) -> Callable:
    """Decorator to setup and cleanup signal handlers for experiment execution.

    This decorator automatically:
    1. Sets up SIGINT and SIGTERM handlers before execution
    2. Cleans up signal handlers after execution (success or failure)
    3. Ensures proper resource cleanup

    Args:
        func: The method to decorate (typically the run method)

    Returns:
        The decorated method with signal handling
    """

    @wraps(func)
    def wrapper(self: ExperimentRunner, *args: Any, **kwargs: Any) -> Any:
        # Setup signal handlers
        self._setup_signal_handlers()

        try:
            # Execute the original method
            return func(self, *args, **kwargs)
        finally:
            # Always cleanup signal handlers
            self._cleanup_signal_handlers()

    return wrapper


class ExperimentRunner:
    """Runs evaluation experiments on datasets using custom tasks and evaluators.

    The ExperimentRunner orchestrates the complete evaluation workflow by:
    1. Processing each dataset item through a custom evaluation task
    2. Running evaluators on the task outputs
    3. Collecting and organizing results with timing and error information
    4. Handling failures gracefully with proper error reporting

    Key Features:
        - **Task Execution**: Runs custom evaluation tasks on dataset items
        - **Evaluator Orchestration**: Executes multiple evaluators on task outputs
        - **Error Handling**: Gracefully handles task and evaluator failures
        - **Result Collection**: Organizes results with timing and status information
        - **Flexible Configuration**: Supports custom parameter mapping for evaluators
        - **Parameter Introspection**: Automatically detects required evaluator parameters

    Use Cases:
        - **Model Evaluation**: Evaluate LLM models on test datasets
        - **A/B Testing**: Compare different model versions or configurations
        - **Quality Assurance**: Validate model performance across different inputs
        - **Benchmarking**: Run standardized evaluations on multiple models

    Args:
        experiment: The experiment entity containing metadata and configuration.
        dataset: The dataset containing test cases to evaluate.
        task: Function that processes dataset items and returns outputs.
        evaluators: List of evaluators to run on task outputs.
        score_fn_kwargs_mapping: Optional mapping for evaluator parameter transformation.


    Note:
        The runner processes dataset items sequentially. For large datasets,
        consider implementing parallel processing or batch processing strategies.
        Do not use this class directly. Use the evaluate function instead.
    """

    def __init__(
        self,
        experiment: Experiment,
        dataset: Dataset,
        task: EvalTaskType,
        evaluators: list[Evaluator],
        score_fn_kwargs_mapping: ScoreFnKwargsMappingType | None = None,
        max_workers: int = 1,
    ) -> None:
        """Initialize the experiment runner with experiment configuration.

        Args:
            experiment: The experiment entity containing metadata and configuration.
            dataset: The dataset containing test cases to evaluate.
            task: Function that processes dataset items and returns outputs.
                Must accept (inputs, extras, metadata) and return dict of outputs.
            evaluators: List of evaluators to run on task outputs.
            score_fn_kwargs_mapping: Optional mapping for transforming evaluator
                parameters. Maps parameter names to either string keys or
                transformation functions.
            max_workers: Maximum number of workers to use for concurrent processing.

        Raises:
            ValueError: If evaluators list is empty or contains invalid evaluators.
            TypeError: If task function has incorrect signature.

        Example:
            >>> def my_eval_task(inputs, extras, metadata):
            ...     return {"answer": "Generated response"}
            >>>
            >>> runner = ExperimentRunner(
            ...     experiment=experiment,
            ...     dataset=dataset,
            ...     task=my_eval_task,
            ...     evaluators=[AnswerRelevance(), Conciseness()],
            ...     score_fn_kwargs_mapping={
            ...         "output": "answer",
            ...         "question": lambda x: x["inputs"]["question"]
            ...     }
            ... )
        """
        self._experiment = experiment
        self._dataset = dataset
        self._task = task
        self._evaluators = evaluators
        self._score_fn_kwargs_mapping = score_fn_kwargs_mapping
        self._result_publisher = ExperimentResultPublisher(experiment=experiment)
        self._max_workers = max_workers

    @cached_property
    def _client(self) -> RequestClient:
        """Get the HTTP client for making API requests."""
        return get_connection().client

    def _setup_signal_handlers(self) -> None:
        """Register signal handlers for graceful shutdown on SIGTERM/SIGINT."""
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def _cleanup_signal_handlers(self) -> None:
        """Restore default signal handlers after experiment completion."""
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)

    def _handle_shutdown(self, signum: int, _frame: Any) -> None:
        """Handle shutdown signal by cancelling the running experiment.

        :param signum: Signal number received
        :param _frame: Signal frame (unused)
        """
        logger.info(
            "Received shutdown signal %s(%d), cancelling experiment - %s",
            self._experiment.name,
            signal.Signals(signum).name,
            signum,
        )

        self._result_publisher.flush()

        self._experiment.update(
            status=ExperimentStatus.CANCELLED,
            error_reason=f"Received shutdown signal {signal.Signals(signum).name}({signum})",
            error_message="Experiment cancelled due to user interruption or system termination",
            traceback=None,
        )

        # Use KeyboardInterrupt for both signals (consistent)
        raise KeyboardInterrupt(
            f"Experiment cancelled due to {signal.Signals(signum).name}({signum})"
        )

    def _run_eval_task(
        self,
        dataset_item: DatasetItem,
    ) -> dict[str, Any]:
        """Execute the evaluation task on a single dataset item.

        Calls the configured evaluation task function with the dataset item's
        inputs, extras, and metadata, returning the generated outputs.

        Args:
            dataset_item: The dataset item to process through the evaluation task.

        Returns:
            dict[str, Any]: The outputs generated by the evaluation task.

        Raises:
            Exception: Any exception raised by the evaluation task function.
        """
        logger.debug("[Test case=%s] Calling eval task function", dataset_item.id)
        start_time = time.monotonic()
        outputs = self._task(  # type: ignore
            inputs=dataset_item.inputs,
            extras=dataset_item.extras,
            metadata=dataset_item.metadata,
        )
        duration = time.monotonic() - start_time
        logger.debug(
            "[Test case=%s] Eval task function completed in %.2f seconds",
            dataset_item.id,
            duration,
        )
        return outputs

    @staticmethod
    def _run_evaluator(
        dataset_item: DatasetItem, evaluator: Evaluator, score_fn_kwargs: dict[str, Any]
    ) -> Score | list[Score]:
        """Execute a single evaluator on a dataset item with error handling.

        Runs the evaluator's score method with the provided arguments and handles
        any exceptions by returning a failed score with error information.

        Args:
            dataset_item: The dataset item being evaluated (for logging).
            evaluator: The evaluator to run.
            score_fn_kwargs: Keyword arguments to pass to the evaluator's score method.

        Returns:
            Score | list[Score]: The score(s) generated by the evaluator, or a
                failed score if an exception occurred.

        Note:
            This method catches all exceptions to ensure that a single evaluator
            failure doesn't stop the entire experiment. Failed evaluators return
            a Score with FAILED status and error information.
        """

        try:
            logger.debug(
                "[Test case=%s] Calling scoring function %s",
                dataset_item.id,
                evaluator.name,
            )
            start_time = time.monotonic()
            result = evaluator.score(**score_fn_kwargs)
            duration = time.monotonic() - start_time
            logger.debug(
                "[Test case=%s] Scoring function %s completed in %.2f seconds",
                dataset_item.id,
                evaluator.name,
                duration,
            )

            return result
        except ScoreFunctionInvalidArgs:
            raise
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(
                "[Test case=%s] Scoring function %s failed: %s",
                dataset_item.id,
                evaluator.name,
                e,
            )
            error = get_error_from_exception(e)
            return Score(
                name=evaluator.name,
                evaluator_name=evaluator.name,
                status=ScoreStatus.FAILED,
                error_reason=error.reason,
                error_message=error.message,
            )

    def _run_evaluators(
        self, dataset_item: DatasetItem, outputs: dict[str, Any]
    ) -> list[Score]:
        """Run all evaluators on a dataset item's outputs.

        Processes the task outputs through all configured evaluators, applying
        any parameter mapping transformations and collecting all scores.

        Args:
            dataset_item: The dataset item being evaluated.
            outputs: The outputs generated by the evaluation task.

        Returns:
            list[Score]: List of all scores generated by the evaluators.

        Raises:
            ValueError: If an evaluator is not a valid Evaluator instance.
        """

        scores = []
        for evaluator in self._evaluators:
            eval_fn_kwargs = self._get_score_fn_kwargs(
                evaluator=evaluator,
                inputs=dataset_item.inputs,
                outputs=outputs,
                expected_outputs=dataset_item.expected_outputs,
                kwargs_mapping=self._score_fn_kwargs_mapping,
            )

            result = self._run_evaluator(
                dataset_item=dataset_item,
                evaluator=evaluator,
                score_fn_kwargs=eval_fn_kwargs,
            )
            scores.extend(result if isinstance(result, list) else [result])

        return scores

    def _run_experiment(
        self,
        dataset_item: DatasetItem,
    ) -> ExperimentItemResult:
        """Run the complete experiment workflow on a single dataset item.

        Executes the evaluation task and all evaluators for a single dataset item,
        handling errors gracefully and tracking timing information.

        Args:
            dataset_item: The dataset item to process through the experiment.

        Returns:
            ExperimentItemResult: The result containing the experiment item and scores.

        Note:
            If the evaluation task fails, the experiment item is marked as FAILED
            and no evaluators are run. If evaluators fail, they return failed scores
            but don't stop the experiment for that item.
        """
        logger.debug("[Test case=%s] Starting experiment", dataset_item.id)
        start_time = time.monotonic()
        experiment_item = NewExperimentItem(
            dataset_item_id=dataset_item.id,
            outputs={},
            status="",  # Fill in the status later
        )

        try:
            outputs = self._run_eval_task(dataset_item=dataset_item)
            experiment_item.outputs = outputs
        except Exception as e:  # pylint: disable=broad-exception-caught
            error = get_error_from_exception(e)
            experiment_item.duration_ms = int((time.monotonic() - start_time) * 1000)
            experiment_item.status = ExperimentItemStatus.FAILED
            experiment_item.set_error(error)

            logger.error(
                "[Test case=%s] Eval task function failed: %s(%s)",
                dataset_item.id,
                error.reason,
                error.message,
            )

            return ExperimentItemResult(
                experiment_item=experiment_item,
                dataset_item=dataset_item,
                scores=[],
            )

        scores = self._run_evaluators(dataset_item=dataset_item, outputs=outputs)

        # Mark the experiment as completed
        duration = time.monotonic() - start_time

        experiment_item.duration_ms = int(duration * 1000)
        experiment_item.status = ExperimentItemStatus.SUCCESS

        logger.debug(
            "[Test case=%s] Experiment completed in %.2f seconds",
            dataset_item.id,
            duration,
        )

        return ExperimentItemResult(
            experiment_item=experiment_item,
            dataset_item=dataset_item,
            scores=scores,
        )

    def _run_experiment_and_publish(
        self,
        dataset_item: DatasetItem,
    ) -> ExperimentItemResult:
        """Run the complete experiment workflow on a single dataset item and publish results."""
        try:
            result = self._run_experiment(dataset_item=dataset_item)

            # Publish the result to the backend.
            self._result_publisher.publish(result)
            return result
        except ScoreFunctionInvalidArgs as e:
            # Stop processing if a score function got invalid arguments.
            error = get_error_from_exception(e)
            logger.error(
                "Scoring function called with invalid arguments: %s(%s)",
                error.reason,
                error.message,
            )
            self._experiment.update(
                status=ExperimentStatus.FAILED,
                error_reason=error.reason,
                error_message=error.message,
                traceback=error.traceback,
            )
            raise e

    @staticmethod
    def _get_score_fn_kwargs(
        evaluator: Evaluator,
        inputs: dict[str, Any],
        outputs: dict[str, Any],
        expected_outputs: dict[str, Any] | None = None,
        kwargs_mapping: ScoreFnKwargsMappingType | None = None,
    ) -> dict[str, Any]:
        """Transform and map parameters for evaluator score functions.

        Creates a base set of keyword arguments from inputs, outputs, and expected
        outputs, then applies mapping transformations from both evaluator-level and
        evaluation-level mappings. The method uses introspection to determine which
        parameters the evaluator's score function requires and only passes those parameters.

        Mapping Priority (highest to lowest):
        1. Evaluator-level score_fn_kwargs_mapping (set in evaluator constructor)
        2. Evaluation-level kwargs_mapping (passed to evaluate function)
        3. Default parameter resolution

        Args:
            evaluator: The evaluator instance containing its own parameter mappings.
            inputs: The input data from the dataset item.
            outputs: The outputs generated by the evaluation task.
            expected_outputs: The expected outputs from the dataset item.
            kwargs_mapping: Optional evaluation-level mapping for parameter transformation.
                Maps parameter names to either string keys or transformation functions.

        Returns:
            dict[str, Any]: The final keyword arguments for the evaluator score function,
                containing only the parameters that the function requires.

        Raises:
            ScoreFunctionInvalidArgs: If required parameters are missing or invalid
                after applying the mapping transformations.

        Example:
            >>> # Evaluator with built-in mapping
            >>> regex_eval = RegexSearch(pattern=r"\\d+", output_key="answer")
            >>> kwargs = _get_score_fn_kwargs(
            ...     evaluator=regex_eval,
            ...     inputs={"question": "What is 2+2?"},
            ...     outputs={"answer": "4"},
            ...     expected_outputs={"answer": "4"}
            ... )
            >>> # Result: {"output": "4"}  # Uses evaluator's output_key mapping
            >>>
            >>> # Override evaluator mapping with evaluation-level mapping
            >>> kwargs = _get_score_fn_kwargs(
            ...     evaluator=regex_eval,
            ...     inputs={"question": "What is 2+2?"},
            ...     outputs={"answer": "4", "response": "The answer is 4"},
            ...     expected_outputs={"answer": "4"},
            ...     kwargs_mapping={"output": "response"}  # Override evaluator's mapping
            ... )
            >>> # Result: {"output": "The answer is 4"}  # Uses evaluation-level override
            >>>
            >>> # Complex mapping with transformation functions
            >>> kwargs = _get_score_fn_kwargs(
            ...     evaluator=AnswerRelevance(),
            ...     inputs={"question": "What is 2+2?"},
            ...     outputs={"answer": "4"},
            ...     expected_outputs={"answer": "4"},
            ...     kwargs_mapping={
            ...         "question": lambda x: x["inputs"]["question"],
            ...         "answer": "answer"
            ...     }
            ... )
            >>> # Result: {"question": "What is 2+2?", "answer": "4"}

        Note:
            This method uses introspection to determine which parameters the score
            function requires, ensuring that only necessary parameters are passed.
            Evaluator-level mappings take precedence over evaluation-level mappings,
            allowing evaluators to define sensible defaults while still permitting
            customization at the evaluation level.
        """

        score_fn = evaluator.fn if isinstance(evaluator, EvalFn) else evaluator.score

        # Note: Don't expand inputs and expected_outputs into kwargs to avoid key collisions with outputs.
        all_kwargs = {
            "inputs": inputs,
            "expected_outputs": expected_outputs,
            "outputs": outputs,
            **outputs,
        }

        # Use ordered dict to preserve the order of kwargs_mapping keys to avoid
        # resolving keys in random order.
        kwargs_mapping = OrderedDict(kwargs_mapping or {})

        # Give evaluator level mapping higher priority than evaluation level mapping.
        kwargs_mapping.update(evaluator.score_fn_kwargs_mapping)

        for key, value in kwargs_mapping.items():
            if callable(value):
                all_kwargs[key] = value(all_kwargs)
            else:
                if value not in all_kwargs:
                    raise ScoreFunctionInvalidArgs(
                        f'Invalid score_fn_kwargs_mapping for evaluator score function "{score_fn.__qualname__}: "{value}" does not exist in outputs.'
                    )
                all_kwargs[key] = all_kwargs.get(value)

        kwargs: dict[str, Any] = {}
        missing_required_args: list[str] = []

        for name, param in inspect.signature(score_fn).parameters.items():
            if (
                param.kind in ALLOWED_PARAM_KINDS
                and param.default == inspect.Parameter.empty
            ):
                if name in all_kwargs:
                    kwargs[name] = all_kwargs.get(name)
                else:
                    missing_required_args.append(name)

        if missing_required_args:
            raise ScoreFunctionInvalidArgs(
                f'Missing required arguments for evaluator score function "{score_fn.__qualname__}": {missing_required_args}'
            )

        return kwargs

    def _validate_eval_task_kwargs(self) -> None:
        """Validate that the evaluation task function has the correct signature.

        Ensures that the evaluation task function accepts exactly the required
        parameters: inputs, extras, and metadata. This validation prevents runtime
        errors by catching signature mismatches early in the experiment setup.

        The method uses introspection to examine the task function's signature
        and validates that it matches the expected EvalTaskType signature:
        (inputs: dict, extras: dict, metadata: dict) -> dict

        Raises:
            TaskFunctionInvalidArgs: If the task function has parameters other than
                the required inputs, extras, and metadata parameters.

        Note:
            This method is called during experiment initialization to ensure
            the task function is compatible with the evaluation framework.
            The validation is performed once per experiment to avoid repeated
            introspection overhead during execution.
        """
        expected_params = {"inputs", "extras", "metadata"}
        try:
            sig = inspect.signature(self._task)

            # Try to bind with the expected parameters
            sig.bind(inputs={}, extras={}, metadata={})

            # Check for extra parameters
            param_names = set(sig.parameters.keys())

            extra_params = param_names - expected_params

            if extra_params:
                raise TaskFunctionInvalidArgs(
                    f'Task function "{self._task.__qualname__}" has unexpected parameters: {extra_params}. '
                    f"Expected only: {expected_params}"
                )

        except TypeError as e:
            # Missing required parameters
            raise TaskFunctionInvalidArgs(
                f'Task function "{self._task.__qualname__}" is missing required parameters. '
                f"Expected: {expected_params}. Original error: {str(e)}"
            ) from e

    @with_signal_handlers
    def run(
        self,
    ) -> ExperimentResult:
        """Run the complete evaluation experiment on all dataset items.

        Processes each dataset item through the evaluation task and runs all
        evaluators on the resulting outputs. Returns a list of results, one
        for each dataset item processed.

        Returns:
            ExperimentResult: List of ExperimentItemResult objects, each containing
                the experiment item data and scores for one dataset item and experiment
                entity.

        Raises:
            RuntimeError: If no connection is available for API calls.
            ValueError: If dataset is empty or evaluators are invalid.
            ScoreFunctionInvalidArgs: If a score function called with invalid arguments.
            TaskFunctionInvalidArgs: If a task function called with invalid arguments.

        Example:
            >>> runner = ExperimentRunner(...)
            >>> results = runner.run()
            >>>
            >>> # Process results
            >>> for result in results:
            ...     item_id = result.experiment_item.dataset_item_id
            ...     status = result.experiment_item.status
            ...     print(f"Item {item_id}: {status}")
            ...
            ...     for score in result.scores:
            ...         print(f"  {score.name}: {score.value} ({score.status})")

        Note:
            This method processes dataset items sequentially. For large datasets,
            consider implementing parallel processing or using batch processing
            strategies to improve performance.
        """
        start_time = time.monotonic()
        logger.info("Starting experiment %s", self._experiment.name)

        try:
            self._validate_eval_task_kwargs()
        except TaskFunctionInvalidArgs as e:
            error = get_error_from_exception(e)
            logger.error(
                "Task function is called with invalid arguments: %s(%s)",
                error.reason,
                error.message,
            )
            self._experiment.update(
                status=ExperimentStatus.FAILED,
                error_reason=error.reason,
                error_message=error.message,
                traceback=error.traceback,
            )
            raise e

        dataset_items = list(self._dataset.get_items())
        logger.info(
            "Loaded %d test cases from %s dataset",
            len(dataset_items),
            self._dataset.name,
        )

        # Mark the experiment as in progress
        self._experiment.update(
            status=ExperimentStatus.IN_PROGRESS,
        )

        # Use a thread pool to process the dataset items when max_workers > 1
        if self._max_workers > 1:
            results = thread_map(
                self._run_experiment_and_publish,
                dataset_items,
                max_workers=self._max_workers,
            )
        else:
            results = [
                self._run_experiment_and_publish(dataset_item)
                for dataset_item in tqdm(
                    dataset_items,
                    desc="Experiment progress",
                    total=len(dataset_items),
                )
            ]

        # Flush the remaining results to the backend.
        self._result_publisher.flush()

        # Mark the experiment as completed
        duration = time.monotonic() - start_time
        self._experiment.update(
            status=ExperimentStatus.COMPLETED,
            duration_ms=int(duration * 1000),
        )

        logger.info(
            "Experiment %s completed in %.2f seconds", self._experiment.name, duration
        )

        logger.info("View the experiment result - %s", self._experiment.get_app_url())

        return ExperimentResult(
            experiment=self._experiment,
            results=results,
        )

    def __call__(self) -> ExperimentResult:
        """Allow the runner to be called directly as a function.

        This provides a convenient way to run the experiment without explicitly
        calling the run() method.

        Returns:
            ExperimentResult: Same as run() method.

        Example:
            >>> runner = ExperimentRunner(...)
            >>> results = runner()  # Equivalent to runner.run()
        """
        return self.run()
