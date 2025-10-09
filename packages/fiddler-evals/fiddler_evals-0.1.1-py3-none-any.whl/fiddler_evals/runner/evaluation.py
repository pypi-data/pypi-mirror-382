from __future__ import annotations

import logging
from datetime import datetime
from typing import Callable

from fiddler_evals.entities.dataset import Dataset
from fiddler_evals.entities.experiment import Experiment
from fiddler_evals.evaluators.base import Evaluator, ScoreFnKwargsMappingType
from fiddler_evals.evaluators.eval_fn import EvalFn
from fiddler_evals.runner.experiment_runner import (
    EvalTaskType,
    ExperimentResult,
    ExperimentRunner,
)

logger = logging.getLogger(__name__)


def evaluate(
    dataset: Dataset,
    task: EvalTaskType,
    evaluators: list[Evaluator | Callable],
    name_prefix: str | None = None,
    description: str | None = None,
    metadata: dict | None = None,
    score_fn_kwargs_mapping: ScoreFnKwargsMappingType | None = None,
    max_workers: int = 1,
) -> ExperimentResult:
    """Evaluate a dataset using a task function and a list of evaluators.

    This is the main entry point for running evaluation experiments. It creates
    an experiment, runs the evaluation task on all dataset items, and executes
    the specified evaluators to generate scores.

    The function automatically:
    1. Creates a new experiment with a unique name
    2. Runs the evaluation task on each dataset item
    3. Executes all evaluators on the task outputs
    4. Returns comprehensive results with timing and error information

    Key Features:
        - **Automatic Experiment Creation**: Creates experiments with unique names
        - **Task Execution**: Runs custom evaluation tasks on dataset items
        - **Evaluator Orchestration**: Executes multiple evaluators on outputs
        - **Error Handling**: Gracefully handles task and evaluator failures
        - **Result Collection**: Returns detailed results with timing information
        - **Flexible Configuration**: Supports custom parameter mapping for evaluators
        - **Concurrent Processing**: Supports concurrent processing of dataset items

    Use Cases:
        - **Model Evaluation**: Evaluate LLM models on test datasets
        - **A/B Testing**: Compare different model versions or configurations
        - **Quality Assurance**: Validate model performance across different inputs
        - **Benchmarking**: Run standardized evaluations on multiple models

    Args:
        dataset: The dataset containing test cases to evaluate.
        task: Function that processes dataset items and returns outputs.
            Must accept (inputs, extras, metadata) and return dict of outputs.
        evaluators: List of evaluators to run on task outputs. Can include
            both Evaluator instances and callable functions.
        name_prefix: Optional prefix for the experiment name. If not provided,
            uses the dataset name as prefix. A unique ID is always appended.
        description: Optional description for the experiment.
        metadata: Optional metadata dictionary for the experiment.
        score_fn_kwargs_mapping: Optional evaluation-level mapping for transforming evaluator
            parameters. Maps parameter names to either string keys or transformation functions.
            This mapping has lower priority than evaluator-level mappings set in the evaluator
            constructor, allowing evaluators to define sensible defaults while still permitting
            customization at the evaluation level.
        max_workers: Maximum number of workers to use for concurrent processing. Use more than 1 only if the
        eval task function is thread-safe.

    Returns:
        ExperimentResult: List of ExperimentItemResult objects, each containing
            the experiment item data and scores for one dataset item.

    Raises:
        ValueError: If dataset is empty or evaluators are invalid.
        RuntimeError: If no connection is available for API calls.
        ApiError: If there's an error creating the experiment or communicating
            with the Fiddler API.

    Example:
        >>> from fiddler_evals import evaluate
        >>> from fiddler_evals.evaluators import AnswerRelevance, Conciseness, RegexSearch
        >>> from fiddler_evals import Dataset
        >>>
        >>> # Get dataset
        >>> dataset = Dataset.get_by_name("my-eval-dataset")
        >>>
        >>> # Define evaluation task
        >>> def eval_task(inputs, extras, metadata):
        ...     # Your model inference logic here
        ...     question = inputs["question"]
        ...     answer = my_model.generate(question)
        ...     return {"answer": answer, "question": question}
        >>>
        >>> # Example 1: Basic evaluation with parameter mapping
        >>> results = evaluate(
        ...     dataset=dataset,
        ...     task=eval_task,
        ...     evaluators=[AnswerRelevance(), Conciseness()],
        ...     name_prefix="my-model-eval",
        ...     description="Evaluation of my model on Q&A dataset",
        ...     metadata={"model_version": "v1.0", "temperature": 0.7},
        ...     score_fn_kwargs_mapping={
        ...         "output": "answer",
        ...         "question": lambda x: x["inputs"]["question"]
        ...     }
        ... )
        >>>
        >>> # Example 2: Multiple evaluator instances with score_name_prefix for differentiation
        >>> evaluators = [
        ...     RegexSearch(
        ...         r"\\d+",
        ...         score_name_prefix="question",
        ...         score_name="has_number",
        ...         score_fn_kwargs_mapping={"output": "question"}
        ...     ),
        ...     RegexSearch(
        ...         r"\\d+",
        ...         score_name_prefix="answer",
        ...         score_name="has_number",
        ...         score_fn_kwargs_mapping={"output": "answer"}
        ...     )
        ... ]
        >>> results = evaluate(
        ...     dataset=dataset,
        ...     task=eval_task,
        ...     evaluators=evaluators,
        ...     score_fn_kwargs_mapping={
        ...         "question": lambda x: x["inputs"]["question"],
        ...         # Note: "answer" mapping not needed since evaluator defines it
        ...     }
        ... )
        >>> # Process results
        >>> for result in results:
        ...     item_id = result.experiment_item.dataset_item_id
        ...     status = result.experiment_item.status
        ...     print(f"Item {item_id}: {status}")
        ...
        ...     for score in result.scores:
        ...         print(f"  {score.name}: {score.value} ({score.status})")


    Note:
        The function processes dataset items sequentially. For large datasets,
        consider implementing parallel processing or batch processing strategies.
        The experiment name is automatically made unique by appending datetime.

        Parameter Mapping Priority:
        When both evaluator-level and evaluation-level mappings are present,
        evaluator-level mappings take precedence. This allows evaluators to define
        sensible defaults while still permitting customization at the evaluation level.

        Mapping Priority (highest to lowest):
        1. Evaluator-level score_fn_kwargs_mapping (set in evaluator constructor)
        2. Evaluation-level score_fn_kwargs_mapping (passed to evaluate function)
        3. Default parameter resolution
    """

    name_suffix = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if name_prefix:
        # Suffix datetime to make sure the name is unique across multiple evaluations.
        name = f"{name_prefix}:{name_suffix}"
    else:
        name = f"{dataset.name}:{name_suffix}"

    experiment = Experiment.create(
        name=name,
        application_id=dataset.application.id,
        dataset_id=dataset.id,
        description=description,
        metadata=metadata,
    )

    logger.info(
        "Created experiment %s(id=%s) for dataset %s(id=%s)",
        name,
        experiment.id,
        dataset.name,
        dataset.id,
    )

    # Wrap the user-defined function with EvalFn
    _evaluators = [EvalFn(item) if callable(item) else item for item in evaluators]

    runner = ExperimentRunner(
        experiment=experiment,
        dataset=dataset,
        task=task,
        evaluators=_evaluators,
        score_fn_kwargs_mapping=score_fn_kwargs_mapping,
        max_workers=max_workers,
    )

    return runner()


# Alias
run_experiment = evaluate
