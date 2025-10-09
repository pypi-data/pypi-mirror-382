"""
Experiment entity for tracking and managing evaluation runs in Fiddler.

The Experiment class represents a single evaluation run of a test suite against
a specific application/LLM/Agent version and evaluators. Experiments provide tracking, monitoring,
and result management for GenAI evaluation workflows within the Fiddler platform.

Key Concepts:
    - **Evaluation Tracking**: Experiments track individual evaluation runs and their results
    - **Status Management**: Experiments have lifecycle states (PENDING, IN_PROGRESS, COMPLETED, etc.)
    - **Dataset Integration**: Experiments are linked to specific datasets for evaluation
    - **Result Storage**: Experiments store evaluation results, metrics, and error information

Common Workflow:
    1. Create or retrieve a dataset with test cases
    2. Create an experiment using Experiment.create() with the dataset via evaluate() method
    3. Monitor experiment status and progress
    4. Retrieve evaluation results and metrics
    5. Analyze and compare experiment results

Example:
    # List experiments
    experiments = Experiment.list(
        application_id=application_id,
        dataset_id=dataset_id
    )

Note:
    Experiment names must be unique within an application. Experiments track the complete
    lifecycle of evaluation runs from creation to completion or failure.
"""

from __future__ import annotations

import builtins
import enum
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterator
from uuid import UUID

from fiddler_evals.constants import CONTENT_TYPE_HEADER_KEY, JSON_CONTENT_TYPE
from fiddler_evals.decorators import handle_api_error
from fiddler_evals.entities.base import BaseEntity
from fiddler_evals.exceptions import NotFound
from fiddler_evals.pydantic_models.compact import (
    ApplicationCompact,
    DatasetCompact,
    ProjectCompact,
    UserCompact,
)
from fiddler_evals.pydantic_models.experiment import (
    ExperimentItem,
    ExperimentItemResult,
    ExperimentResponse,
    NewExperimentItem,
)
from fiddler_evals.pydantic_models.filter_query import (
    OperatorType,
    QueryCondition,
    QueryRule,
)

logger = logging.getLogger(__name__)


class ExperimentStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ExperimentItemStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class Experiment(BaseEntity):
    """Represents an Experiment for tracking evaluation runs and results.

    An Experiment is a single evaluation run of a test suite against a specific
    application/LLM/Agent version and evaluators. Experiments provide comprehensive tracking,
    monitoring, and result management for GenAI evaluation workflows, enabling
    systematic testing and performance analysis.

    Key Features:
        - **Evaluation Tracking**: Complete lifecycle tracking of evaluation runs
        - **Status Management**: Real-time status updates (PENDING, IN_PROGRESS, COMPLETED, etc.)
        - **Dataset Integration**: Linked to specific datasets for evaluation
        - **Result Storage**: Comprehensive storage of results, metrics, and error information
        - **Error Handling**: Detailed error tracking with traceback information

    Experiment Lifecycle:
        1. **Creation**: Create experiment with dataset and application references
        2. **Execution**: Experiment runs evaluation against the dataset
        3. **Monitoring**: Track status and progress in real-time
        4. **Completion**: Retrieve results, metrics, and analysis
        5. **Cleanup**: Archive or delete completed experiments

    Attributes:
        id (UUID): Unique experiment identifier, assigned by server on creation.
        name (str): Experiment name, must be unique within the application.
        status (ExperimentStatus): Current status of the experiment (PENDING, IN_PROGRESS, etc.).
        description (str, optional): Human-readable description of the experiment.
        error_reason (str, optional): Reason for experiment failure, if applicable.
        error_message (str, optional): Detailed error message, if applicable.
        traceback (str, optional): Full error traceback, if applicable.
        metadata (dict): Custom metadata dictionary for additional experiment information.
        created_at (datetime): Experiment creation timestamp.
        updated_at (datetime): Last modification timestamp.
        created_by (UserCompact): User who created the experiment.
        updated_by (UserCompact): User who last updated the experiment.
        project (ProjectCompact): Project containing this experiment.
        application (ApplicationCompact): Application being evaluated.
        dataset (DatasetCompact): Dataset used for evaluation.

    Example:
        # Use this class to list
        experiments = Experiment.list(
            application_id=application_id,
            dataset_id=dataset_id,
        )

    Note:
        Experiments are permanent records of evaluation runs. Once created, the name
        cannot be changed, but metadata and description can be updated. Failed
        experiments retain error information for debugging and analysis.
    """

    id: UUID
    name: str
    status: str
    created_at: datetime
    updated_at: datetime
    created_by: UserCompact
    updated_by: UserCompact
    project: ProjectCompact
    application: ApplicationCompact
    dataset: DatasetCompact
    description: str | None = None
    error_reason: str | None = None
    error_message: str | None = None
    traceback: str | None = None
    duration_ms: int | None = None
    metadata: dict = field(default_factory=dict)

    @staticmethod
    def _get_url(id_: UUID | str | None = None) -> str:
        """Get experiment resource/item url"""
        url = "/v3/evals/experiments"
        return url if not id_ else f"{url}/{id_}"

    @classmethod
    def _from_dict(cls, data: dict) -> Experiment:
        """Build the entity object from the given dictionary"""

        # Deserialize the response
        response_obj = ExperimentResponse(**data)

        # Initialize
        instance = cls(
            id=response_obj.id,
            name=response_obj.name,
            description=response_obj.description,
            metadata=response_obj.metadata,
            status=response_obj.status,
            duration_ms=response_obj.duration_ms,
            error_reason=response_obj.error_reason,
            error_message=response_obj.error_message,
            traceback=response_obj.traceback,
            created_at=response_obj.created_at,
            updated_at=response_obj.updated_at,
            created_by=response_obj.created_by,
            updated_by=response_obj.updated_by,
            project=response_obj.project,
            application=response_obj.application,
            dataset=response_obj.dataset,
        )

        return instance

    def get_app_url(self) -> str:
        """Get the application URL for this experiment"""
        base_url = self._connection().url.rstrip("/")
        return f"{base_url}/evals/experiments/{self.id}"

    @classmethod
    @handle_api_error
    def get_by_id(cls, id_: UUID | str) -> Experiment:
        """Retrieve an experiment by its unique identifier.

        Fetches an experiment from the Fiddler platform using its UUID. This is the most
        direct way to retrieve an experiment when you know its ID.

        Args:
            id_: The unique identifier (UUID) of the experiment to retrieve.
                Can be provided as a UUID object or string representation.

        Returns:
            :class:`~fiddler.entities.Experiment`: The experiment instance with all metadata and configuration.

        Raises:
            NotFound: If no experiment exists with the specified ID.
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get experiment by UUID
            experiment = Experiment.get_by_id(id_="550e8400-e29b-41d4-a716-446655440000")
            print(f"Retrieved experiment: {experiment.name}")
            print(f"Status: {experiment.status}")
            print(f"Created: {experiment.created_at}")
            print(f"Application: {experiment.application.name}")

        Note:
            This method makes an API call to fetch the latest experiment state from the server.
            The returned experiment instance reflects the current state in Fiddler.
        """
        response = cls._client().get(url=cls._get_url(id_))
        return cls._from_response(response=response)

    @classmethod
    @handle_api_error
    def get_by_name(cls, name: str, application_id: UUID | str) -> Experiment:
        """Retrieve an experiment by name within an application.

        Finds and returns an experiment using its name within the specified application.
        This is useful when you know the experiment name and application but not its UUID.
        Experiment names are unique within an application, making this a reliable lookup method.

        Args:
            name: The name of the experiment to retrieve. Experiment names are unique
                 within an application and are case-sensitive.
            application_id: The UUID of the application containing the experiment.
                          Can be provided as a UUID object or string representation.

        Returns:
            :class:`~fiddler.entities.Experiment`: The experiment instance matching the specified name.

        Raises:
            NotFound: If no experiment exists with the specified name in the application.
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get application instance
            application = Application.get_by_name(name="fraud-detection-app", project_id=project_id)

            # Get experiment by name within an application
            experiment = Experiment.get_by_name(
                name="fraud-detection-eval-v1",
                application_id=application.id
            )
            print(f"Found experiment: {experiment.name} (ID: {experiment.id})")
            print(f"Status: {experiment.status}")
            print(f"Created: {experiment.created_at}")
            print(f"Dataset: {experiment.dataset.name}")

        Note:
            Experiment names are case-sensitive and must match exactly. Use this method
            when you have a known experiment name from configuration or user input.
        """
        _filter = QueryCondition(
            rules=[
                QueryRule(field="name", operator=OperatorType.EQUAL, value=name),
                QueryRule(
                    field="application_id",
                    operator=OperatorType.EQUAL,
                    value=str(application_id),
                ),
            ]
        )

        response = cls._client().get(
            url=cls._get_url(), params={"filter": _filter.model_dump_json()}
        )
        if response.json()["data"]["total"] == 0:
            raise NotFound(
                message="Experiment not found for the given identifier",
                status_code=404,
                reason="NotFound",
            )

        return cls._from_dict(data=response.json()["data"]["items"][0])

    @classmethod
    @handle_api_error
    def list(
        cls, application_id: UUID | str, dataset_id: UUID | str | None = None
    ) -> Iterator[Experiment]:
        """List all experiments in an application.

        Retrieves all experiments that the current user has access to within the specified
        application. Returns an iterator for memory efficiency when dealing with many experiments.

        Args:
            application_id: The UUID of the application to list experiments from.
                          Can be provided as a UUID object or string representation.
            dataset_id: The UUID of the dataset to list experiments from.
                          Can be provided as a UUID object or string representation.

        Yields:
            :class:`~fiddler.entities.Experiment`: Experiment instances for all accessible experiments in the application.

        Raises:
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get application instance
            application = Application.get_by_name(name="fraud-detection-app", project_id=project_id)
            dataset = Dataset.get_by_name(name="fraud-detection-tests", application_id=application.id)

            # List all experiments in an application
            for experiment in Experiment.list(application_id=application.id, dataset_id=dataset.id):
                print(f"Experiment: {experiment.name}")
                print(f"  ID: {experiment.id}")
                print(f"  Status: {experiment.status}")
                print(f"  Created: {experiment.created_at}")
                print(f"  Dataset: {experiment.dataset.name}")

            # Convert to list for counting and filtering
            experiments = list(Experiment.list(application_id=application.id, dataset_id=dataset.id ))
            print(f"Total experiments in application: {len(experiments)}")

            # Find experiments by status
            completed_experiments = [
                exp for exp in Experiment.list(application_id=application.id, dataset_id=dataset.id)
                if exp.status == ExperimentStatus.COMPLETED
            ]
            print(f"Completed experiments: {len(completed_experiments)}")

            # Find experiments by name pattern
            eval_experiments = [
                exp for exp in Experiment.list(application_id=application.id, dataset_id=dataset.id)
                if "eval" in exp.name.lower()
            ]
            print(f"Evaluation experiments: {len(eval_experiments)}")

        Note:
            This method returns an iterator for memory efficiency. Convert to a list
            with list(Experiment.list(application_id)) if you need to iterate multiple times or get
            the total count. The iterator fetches experiments lazily from the API.
        """
        _filter = QueryCondition(
            rules=[
                QueryRule(
                    field="application_id",
                    operator=OperatorType.EQUAL,
                    value=str(application_id),
                ),
            ]
        )

        if dataset_id:
            _filter.add_rule(
                QueryRule(
                    field="dataset_id",
                    operator=OperatorType.EQUAL,
                    value=str(dataset_id),
                )
            )

        params = {"filter": _filter.model_dump_json()}
        for project in cls._paginate(url=cls._get_url(), params=params):
            yield cls._from_dict(data=project)

    @classmethod
    @handle_api_error
    def create(
        cls,
        name: str,
        application_id: UUID | str,
        dataset_id: UUID | str,
        description: str | None = None,
        metadata: dict | None = None,
    ) -> Experiment:
        """Create a new experiment in an application.

        Creates a new experiment within the specified application on the Fiddler platform.
        The experiment must have a unique name within the application and will be linked
        to the specified dataset for evaluation.

        Note: It is not recommended to use this method directly. Instead, use the evaluate method. Creating
        and managing an experiment without evaluate wrapper is extremely advance usecase and should be avoided.

        Args:
            name: Experiment name, must be unique within the application.
            application_id: The UUID of the application to create the experiment in.
                          Can be provided as a UUID object or string representation.
            dataset_id: The UUID of the dataset to use for evaluation.
                       Can be provided as a UUID object or string representation.
            description: Optional human-readable description of the experiment.
            metadata: Optional custom metadata dictionary for additional experiment information.

        Returns:
            :class:`~fiddler.entities.Experiment`: The newly created experiment instance with server-assigned fields.

        Raises:
            Conflict: If an experiment with the same name already exists in the application.
            ValidationError: If the experiment configuration is invalid (e.g., invalid name format).
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get application and dataset instances
            application = Application.get_by_name(name="fraud-detection-app", project_id=project_id)
            dataset = Dataset.get_by_name(name="fraud-detection-tests", application_id=application.id)

            # Create a new experiment for fraud detection evaluation
            experiment = Experiment.create(
                name="fraud-detection-eval-v1",
                application_id=application.id,
                dataset_id=dataset.id,
                description="Comprehensive evaluation of fraud detection model v1.0",
                metadata={"model_version": "1.0", "evaluation_type": "comprehensive", "baseline": "true"}
            )
            print(f"Created experiment with ID: {experiment.id}")
            print(f"Status: {experiment.status}")
            print(f"Created at: {experiment.created_at}")
            print(f"Application: {experiment.application.name}")
            print(f"Dataset: {experiment.dataset.name}")

        Note:
            After successful creation, the experiment instance is returned with
            server-assigned metadata. The experiment is immediately available
            for execution and monitoring. The initial status will be PENDING.
        """
        response = cls._client().post(
            url=cls._get_url(),
            json={
                "name": name,
                "application_id": str(application_id),
                "dataset_id": str(dataset_id),
                "description": description,
                "metadata": metadata or {},
            },
        )

        experiment = cls._from_response(response=response)
        logger.info(
            "Experiment created with id=%s, name=%s", experiment.id, experiment.name
        )
        return experiment

    @classmethod
    @handle_api_error
    def get_or_create(
        cls,
        name: str,
        application_id: UUID | str,
        dataset_id: UUID | str,
        description: str | None = None,
        metadata: dict | None = None,
    ) -> Experiment:
        """Get an existing experiment by name or create a new one if it doesn't exist.

        This is a convenience method that attempts to retrieve an experiment by name
        within an application, and if not found, creates a new experiment with that name.
        Useful for idempotent experiment setup in automation scripts and deployment pipelines.

        Args:
            name: The name of the experiment to retrieve or create.
            application_id: The UUID of the application to search/create the experiment in.
                          Can be provided as a UUID object or string representation.
            dataset_id: The UUID of the dataset to use for evaluation.
                       Can be provided as a UUID object or string representation.
            description: Optional human-readable description of the experiment.
            metadata: Optional custom metadata dictionary for additional experiment information.

        Returns:
            :class:`~fiddler.entities.Experiment`: Either the existing experiment with the specified name,
                  or a newly created experiment if none existed.

        Raises:
            ValidationError: If the experiment name format is invalid.
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get application and dataset instances
            application = Application.get_by_name(name="fraud-detection-app", project_id=project_id)
            dataset = Dataset.get_by_name(name="fraud-detection-tests", application_id=application.id)

            # Safe experiment setup - get existing or create new
            experiment = Experiment.get_or_create(
                name="fraud-detection-eval-v1",
                application_id=application.id,
                dataset_id=dataset.id,
                description="Comprehensive evaluation of fraud detection model v1.0",
                metadata={"model_version": "1.0", "evaluation_type": "comprehensive"}
            )
            print(f"Using experiment: {experiment.name} (ID: {experiment.id})")

            # Idempotent setup in deployment scripts
            experiment = Experiment.get_or_create(
                name="llm-benchmark-eval",
                application_id=application.id,
                dataset_id=dataset.id,
                metadata={"baseline": "true"}
            )

            # Use in configuration management
            model_versions = ["v1.0", "v1.1", "v2.0"]
            experiments = {}
            for version in model_versions:
                experiments[version] = Experiment.get_or_create(
                    name=f"fraud-detection-eval-{version}",
                    application_id=application.id,
                    dataset_id=dataset.id,
                    metadata={"model_version": version}
                )

        Note:
            This method is idempotent - calling it multiple times with the same name
            and application_id will return the same experiment. It logs when creating a new
            experiment for visibility in automation scenarios.
        """
        try:
            return cls.get_by_name(name=name, application_id=application_id)
        except NotFound:
            logger.info("Experiment not found, creating a new one - %s", name)
            return Experiment.create(
                name=name,
                application_id=application_id,
                dataset_id=dataset_id,
                description=description,
                metadata=metadata,
            )

    @handle_api_error
    def update(
        self,
        description: str | None = None,
        metadata: dict | None = None,
        status: ExperimentStatus | None = None,
        error_reason: str | None = None,
        error_message: str | None = None,
        traceback: str | None = None,
        duration_ms: int | None = None,
    ) -> Experiment:
        """Update experiment description, metadata, and status.

        Updates the experiment's description, metadata, and/or status. This method allows
        you to modify the experiment's configuration after creation, including updating
        the experiment status and error information for failed experiments.

        Args:
            description: Optional new description for the experiment. If provided,
                        replaces the existing description. Set to empty string to clear.
            metadata: Optional new metadata dictionary for the experiment. If provided,
                     replaces the existing metadata completely. Use empty dict to clear.
            status: Optional new status for the experiment. Can be used to update
                   experiment status (e.g., PENDING, RUNNING, COMPLETED, FAILED).
            error_reason: Required when status is FAILED. The reason for the experiment failure.
            error_message: Required when status is FAILED. Detailed error message for the failure.
            traceback: Required when status is FAILED. Stack trace information for debugging.
            duration_ms: Optional duration in milliseconds for the experiment execution

        Returns:
            :class:`~fiddler.entities.Experiment`: The updated experiment instance with new metadata and configuration.

        Raises:
            ValueError: If no update parameters are provided (all are None) or if status is FAILED
                       but error_reason, error_message, or traceback are missing.
            ValidationError: If the update data is invalid (e.g., invalid metadata format).
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get existing experiment
            experiment = Experiment.get_by_name(name="fraud-detection-eval-v1", application_id=application_id)

            # Update description and metadata
            updated_experiment = experiment.update(
                description="Updated comprehensive evaluation of fraud detection model v1.1",
                metadata={"model_version": "1.1", "evaluation_type": "comprehensive", "updated_by": "john_doe"}
            )
            print(f"Updated experiment: {updated_experiment.name}")
            print(f"New description: {updated_experiment.description}")

            # Update only metadata
            experiment.update(metadata={"last_updated": "2024-01-15", "status": "active"})

            # Update experiment status to completed
            experiment.update(status=ExperimentStatus.COMPLETED)

            # Mark experiment as failed with error details
            experiment.update(
                status=ExperimentStatus.FAILED,
                error_reason="Evaluation timeout",
                error_message="The evaluation process exceeded the maximum allowed time",
                traceback="Traceback (most recent call last):\n  File \"evaluate.py\", line 42..."
            )

            # Clear description
            experiment.update(description="")

            # Batch update multiple experiments
            for experiment in Experiment.list(application_id=application_id):
                if experiment.status == ExperimentStatus.COMPLETED:
                    experiment.update(metadata={"archived": "true"})

        Note:
            This method performs a complete replacement of the specified fields.
            For partial updates, retrieve current values, modify them, and pass
            the complete new values. The experiment name and ID cannot be changed.
            When updating status to FAILED, all error-related parameters are required.
        """

        payload: dict[str, Any] = {}
        if description is not None:
            payload["description"] = description
        if metadata is not None:
            payload["metadata"] = metadata

        if status is not None:
            payload["status"] = status.value

        if status == ExperimentStatus.FAILED:
            if error_reason is None or error_message is None or traceback is None:
                raise ValueError(
                    "error_reason, error_message, and traceback must be provided"
                )

            payload["error_reason"] = error_reason
            payload["error_message"] = error_message
            payload["traceback"] = traceback

        if duration_ms is not None:
            payload["duration_ms"] = duration_ms

        if not payload:
            raise ValueError("No update parameters provided.")

        response = self._client().patch(
            url=self._get_url(self.id),
            json=payload,
        )
        return self._from_response(response=response)

    @handle_api_error
    def delete(
        self,
    ) -> None:
        """Delete the experiment.

        Permanently deletes the experiment and all associated data from the Fiddler platform.
        This action cannot be undone and will remove all experiment results, metrics, and metadata.

        Raises:
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get existing experiment
            experiment = Experiment.get_by_name(name="fraud-detection-eval-v1", application_id=application_id)

            # Delete the experiment
            experiment.delete()
            print("Experiment deleted successfully")

            # Delete multiple experiments
            for experiment in Experiment.list(application_id=application_id):
                if experiment.status == ExperimentStatus.FAILED:
                    print(f"Deleting failed experiment: {experiment.name}")
                    experiment.delete()

        Note:
            This operation is irreversible. Once deleted, the experiment and all its
            associated data cannot be recovered. Consider archiving experiments instead
            of deleting them if you need to preserve historical data.
        """
        self._client().delete(
            url=self._get_url(self.id),
        )

    @handle_api_error
    def add_items(
        self,
        items: builtins.list[NewExperimentItem],
    ) -> builtins.list[UUID]:
        """Add outputs of LLM/Agent/Application against dataset items to the experiment.

        Adds outputs of LLM/Agent/Application (task or target function) against dataset items to the experiment, representing individual
        test case outcomes. Each item contains the outputs of LLM/Agent/Application results, timing information, and status for a specific dataset item.

        Args:
            items: List of NewExperimentItem instances containing outputs of LLM/Agent/Application against dataset items.
                  Each item should include:
                  - dataset_item_id: UUID of the dataset item being evaluated
                  - outputs: Dictionary containing the outputs of the task function against dataset item
                  - duration_ms: Duration of the execution in milliseconds:
                  - status: Status of the outputs of the task function / scoring against dataset item (PENDING, COMPLETED, FAILED, etc.)
                  - error_reason: Reason for failure, if applicable
                  - error_message: Detailed error message, if applicable

        Returns:
            builtins.list[UUID]: List of UUIDs for the newly created experiment items.

        Raises:
            ValueError: If the items list is empty.
            ValidationError: If any item data is invalid (e.g., missing required fields).
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get existing experiment
            experiment = Experiment.get_by_name(name="fraud-detection-eval-v1", application_id=application_id)

            # Create evaluation result items
            from fiddler_evals.pydantic_models.experiment import NewExperimentItem
            from datetime import datetime, timezone

            items = [
                NewExperimentItem(
                    dataset_item_id=dataset_item_id_1,
                    outputs={"answer": "The watermelon seeds pass through your digestive system"},
                    duration_ms=1000,
                    end_time=datetime.now(tz=timezone.utc),
                    status="COMPLETED",
                    error_reason=None,
                    error_message=None
                ),
                NewExperimentItem(
                    dataset_item_id=dataset_item_id_2,
                    outputs={"answer": "The precise origin of fortune cookies is unclear"},
                    duration_ms=1000,
                    end_time=datetime.now(tz=timezone.utc),
                    status="COMPLETED",
                    error_reason=None,
                    error_message=None
                )
            ]

            # Add items to experiment
            item_ids = experiment.add_items(items)
            print(f"Added {len(item_ids)} evaluation result items")
            print(f"Item IDs: {item_ids}")

            # Add items from evaluation results
            items = [
                {
                    "dataset_item_id": str(dataset_item_id),
                    "outputs": {"answer": result["answer"]},
                    "duration_ms": result["duration_ms"],
                    "end_time": result["end_time"],
                    "status": "COMPLETED"
                }
                for result in items
            ]
            item_ids = experiment.add_items([NewExperimentItem(**item) for item in items])

            # Batch add items with error handling
            try:
                item_ids = experiment.add_items(items)
                print(f"Successfully added {len(item_ids)} items")
            except ValueError as e:
                print(f"Validation error: {e}")
            except Exception as e:
                print(f"Failed to add items: {e}")

        Note:
            This method is typically used after running evaluations to store the results
            in the experiment. Each item represents the evaluation of a single dataset
            item and contains all relevant timing, output, and status information.
        """
        if not items:
            raise ValueError("Items cannot be empty")

        serialized_items = [item.model_dump() for item in items]

        response = self._client().post(
            url=f"{self._get_url(self.id)}/items",
            data={
                "items": serialized_items,
            },
            headers={CONTENT_TYPE_HEADER_KEY: JSON_CONTENT_TYPE},
        )
        return [UUID(id_) for id_ in response.json()["data"]["ids"]]

    @handle_api_error
    def get_items(self) -> Iterator[ExperimentItem]:
        """Retrieve all experiment result items from the experiment.

        Fetches all experiment result items (outputs, timing, status) that were generated
        by the task function against dataset items. Returns an iterator for memory efficiency
        when dealing with large experiments containing many result items.

        Returns:
            Iterator[:class:`~fiddler.pydantic_models.experiment.ExperimentItem`]: Iterator of
                ExperimentItem instances for all result items in the experiment.

        Raises:
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get existing experiment
            experiment = Experiment.get_by_name(name="fraud-detection-eval-v1", application_id=application_id)

            # Get all result items from the experiment
            for item in experiment.get_items():
                print(f"Item ID: {item.id}")
                print(f"Dataset Item ID: {item.dataset_item_id}")
                print(f"Outputs: {item.outputs}")
                print(f"Status: {item.status}")
                print(f"Duration: {item.duration_ms}")
                if item.error_reason:
                    print(f"Error: {item.error_reason} - {item.error_message}")
                print("---")

            # Convert to list for analysis
            all_items = list(experiment.get_items())
            print(f"Total result items: {len(all_items)}")

            # Filter items by status
            completed_items = [
                item for item in experiment.get_items()
                if item.status == "COMPLETED"
            ]
            print(f"Completed items: {len(completed_items)}")

            # Filter items by error status
            failed_items = [
                item for item in experiment.get_items()
                if item.status == "FAILED"
            ]
            print(f"Failed items: {len(failed_items)}")

            # Process items in batches
            batch_size = 100
            for i, item in enumerate(experiment.get_items()):
                if i % batch_size == 0:
                    print(f"Processing batch {i // batch_size + 1}")
                # Process item...

            # Analyze outputs
            for item in experiment.get_items():
                if item.outputs.get("confidence", 0) < 0.8:
                    print(f"Low confidence item: {item.id}")

        Note:
            This method returns an iterator for memory efficiency. Convert to a list
            with list(experiment.get_items()) if you need to iterate multiple times or get
            the total count. The iterator fetches items lazily from the API.
        """
        for item in self._paginate(url=f"{self._get_url(self.id)}/items"):
            yield ExperimentItem(**item)

    @handle_api_error
    def add_results(
        self,
        items: builtins.list[ExperimentItemResult],
    ) -> None:
        """Add evaluation results to the experiment.

        Adds complete evaluation results to the experiment, including both the experiment
        item data (outputs, timing, status) and all associated evaluator scores. This
        method is typically used after running evaluations to store the complete results
        of the evaluation process for a batch of dataset items.

        This method will only append the results to the experiment.

        Note: It is not recommended to use this method directly. Instead, use the evaluate method. Creating
        and managing an experiment without evaluate wrapper is extremely advance usecase and should be avoided.


        Args:
            items: List of ExperimentItemResult instances containing:
                - experiment_item: NewExperimentItem with outputs, timing, and status
                - scores: List of Score objects from evaluators for this item

        Returns:
            None: Results are added to the experiment on the server.

        Raises:
            ValueError: If the items list is empty.
            ValidationError: If any item data is invalid (e.g., missing required fields).
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get existing experiment
            experiment = Experiment.get_by_name(name="fraud-detection-eval-v1", application_id=application_id)

            # Create experiment item with outputs
            experiment_item = NewExperimentItem(
                dataset_item_id=dataset_item.id,
                outputs={"prediction": "fraud", "confidence": 0.95},
                duration_ms=1000,
                end_time=datetime.now(tz=timezone.utc),
                status="COMPLETED"
            )

            # Create scores from evaluators
            scores = [
                Score(
                    name="accuracy",
                    evaluator_name="AccuracyEvaluator",
                    value=1.0,
                    label="Correct",
                    reasoning="Prediction matches ground truth"
                ),
                Score(
                    name="confidence",
                    evaluator_name="ConfidenceEvaluator",
                    value=0.95,
                    label="High",
                    reasoning="High confidence in prediction"
                )
            ]

            # Create result combining item and scores
            result = ExperimentItemResult(
                experiment_item=experiment_item,
                scores=scores
            )

            # Add results to experiment
            experiment.add_results([result])

        Note:
            This method is typically called after running evaluations to store complete
            results. The results include both the experiment item data and all evaluator
            scores, providing a complete record of the evaluation process.
        """
        if not items:
            raise ValueError("Items cannot be empty")

        serialized_items = [item.model_dump(exclude={"dataset_item"}) for item in items]

        self._client().post(
            url=f"{self._get_url(self.id)}/results",
            data={
                "results": serialized_items,
            },
            headers={CONTENT_TYPE_HEADER_KEY: JSON_CONTENT_TYPE},
        )
