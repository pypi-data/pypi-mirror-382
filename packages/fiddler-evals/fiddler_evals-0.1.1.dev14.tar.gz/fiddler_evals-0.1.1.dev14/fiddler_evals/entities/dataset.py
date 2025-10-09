"""
Dataset entity for organizing and managing evaluation datasets in Fiddler.

The Dataset class represents a logical container for organizing evaluation test cases
with inputs and expected outputs. Datasets provide structured storage for GenAI evaluation
data, enabling systematic testing and validation of GenAI applications within the Fiddler platform.

Key Concepts:
    - **Application Container**: Datasets are contained within applications and inherit application-level settings
    - **Test Case Storage**: Datasets store structured test cases with inputs and expected outputs
    - **Metadata Management**: Datasets support custom metadata and tagging for organization
    - **Evaluation Context**: Datasets provide the foundation for GenAI application evaluation

Common Workflow:
    1. Create or retrieve an application for your GenAI use case
    2. Create datasets within the application using Dataset.create()
    3. Add test cases with inputs and expected outputs to the dataset
    4. Use datasets for evaluation and testing of GenAI applications

Example:
    # Create a new dataset within an application
    dataset = Dataset.create(name="fraud_detection_tests", application_id=application_id)

Note:
    Dataset names must be unique within an application. Datasets cannot be renamed
    after creation, but can be deleted if no longer needed.
"""
# pylint: disable=too-many-lines

from __future__ import annotations

import builtins
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterator
from uuid import UUID, uuid4

from fiddler_evals.constants import CONTENT_TYPE_HEADER_KEY, JSON_CONTENT_TYPE
from fiddler_evals.decorators import handle_api_error
from fiddler_evals.entities.base import BaseEntity
from fiddler_evals.exceptions import NotFound
from fiddler_evals.pydantic_models.compact import (
    ApplicationCompact,
    ProjectCompact,
    UserCompact,
)
from fiddler_evals.pydantic_models.dataset import (
    DatasetItem,
    DatasetResponse,
    NewDatasetItem,
)
from fiddler_evals.pydantic_models.filter_query import (
    OperatorType,
    QueryCondition,
    QueryRule,
)
from fiddler_evals.utils.pd import validate_pandas_installation

if TYPE_CHECKING:
    import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class Dataset(BaseEntity):
    """Represents a Dataset container for organizing evaluation test cases.

    A Dataset is a logical container within an Application that stores structured
    test cases with inputs and expected outputs for GenAI evaluation. Datasets provide
    organized storage, metadata management, and tagging capabilities for systematic
    testing and validation of GenAI applications.

    Key Features:
        - **Test Case Storage**: Container for structured evaluation test cases
        - **Application Context**: Datasets are scoped within applications for isolation
        - **Metadata Management**: Custom metadata and tagging for organization
        - **Evaluation Foundation**: Structured data for GenAI application testing
        - **Lifecycle Management**: Coordinated creation, updates, and deletion of datasets

    Dataset Lifecycle:
        1. **Creation**: Create dataset with unique name within an application
        2. **Configuration**: Add test cases and metadata
        3. **Evaluation**: Use dataset for testing GenAI applications
        4. **Maintenance**: Update test cases and metadata as needed
        5. **Cleanup**: Delete dataset when no longer needed

    Attributes:
        id (UUID): Unique dataset identifier, assigned by server on creation.
        name (str): Dataset name, must be unique within the application.
        description (str, optional): Human-readable description of the dataset.
        metadata (dict): Custom metadata dictionary for additional dataset information.
        created_at (datetime): Dataset creation timestamp.
        updated_at (datetime): Last modification timestamp.
        created_by (UserCompact): User who created the dataset.
        updated_by (UserCompact): User who last updated the dataset.
        project (ProjectCompact): Project containing this dataset.
        application (ApplicationCompact): Application containing this dataset.

    Example:
        # Create a new dataset for fraud detection tests
        dataset = Dataset.create(
            name="fraud-detection-tests",
            application_id=application_id,
            description="Test cases for fraud detection model",
            metadata={"source": "production", "version": "1.0"},
        )
        print(f"Created dataset: {dataset.name} (ID: {dataset.id})")

    Note:
        Datasets are permanent containers - once created, the name cannot be changed.
        Deleting a dataset removes all contained test cases and metadata.
        Consider the organizational structure carefully before creating datasets.
    """

    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
    created_by: UserCompact
    updated_by: UserCompact
    project: ProjectCompact
    application: ApplicationCompact
    active: bool = True
    description: str | None = None
    metadata: dict = field(default_factory=dict)

    @staticmethod
    def _get_url(id_: UUID | str | None = None) -> str:
        """Get dataset resource/item url"""
        url = "/v3/evals/datasets"
        return url if not id_ else f"{url}/{id_}"

    @classmethod
    def _from_dict(cls, data: dict) -> Dataset:
        """Build the entity object from the given dictionary"""

        # Deserialize the response
        response_obj = DatasetResponse(**data)

        # Initialize
        instance = cls(
            id=response_obj.id,
            name=response_obj.name,
            description=response_obj.description,
            metadata=response_obj.metadata,
            active=response_obj.active,
            created_at=response_obj.created_at,
            updated_at=response_obj.updated_at,
            created_by=response_obj.created_by,
            updated_by=response_obj.updated_by,
            project=response_obj.project,
            application=response_obj.application,
        )

        return instance

    @classmethod
    @handle_api_error
    def get_by_id(cls, id_: UUID | str) -> Dataset:
        """Retrieve a dataset by its unique identifier.

        Fetches a dataset from the Fiddler platform using its UUID. This is the most
        direct way to retrieve a dataset when you know its ID.

        Args:
            id_: The unique identifier (UUID) of the dataset to retrieve.
                Can be provided as a UUID object or string representation.

        Returns:
            :class:`~fiddler.entities.Dataset`: The dataset instance with all metadata and configuration.

        Raises:
            NotFound: If no dataset exists with the specified ID.
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get dataset by UUID
            dataset = Dataset.get_by_id(id_="550e8400-e29b-41d4-a716-446655440000")
            print(f"Retrieved dataset: {dataset.name}")
            print(f"Created: {dataset.created_at}")
            print(f"Application: {dataset.application.name}")

        Note:
            This method makes an API call to fetch the latest dataset state from the server.
            The returned dataset instance reflects the current state in Fiddler.
        """
        response = cls._client().get(url=cls._get_url(id_))
        return cls._from_response(response=response)

    @classmethod
    @handle_api_error
    def get_by_name(cls, name: str, application_id: UUID | str) -> Dataset:
        """Retrieve a dataset by name within an application.

        Finds and returns a dataset using its name within the specified application.
        This is useful when you know the dataset name and application but not its UUID.
        Dataset names are unique within an application, making this a reliable lookup method.

        Args:
            name: The name of the dataset to retrieve. Dataset names are unique
                 within an application and are case-sensitive.
            application_id: The UUID of the application containing the dataset.
                          Can be provided as a UUID object or string representation.

        Returns:
            :class:`~fiddler.entities.Dataset`: The dataset instance matching the specified name.

        Raises:
            NotFound: If no dataset exists with the specified name in the application.
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get application instance
            application = Application.get_by_name(name="fraud-detection-app", project_id=project_id)

            # Get dataset by name within an application
            dataset = Dataset.get_by_name(
                name="fraud-detection-tests",
                application_id=application.id
            )
            print(f"Found dataset: {dataset.name} (ID: {dataset.id})")
            print(f"Created: {dataset.created_at}")
            print(f"Application: {dataset.application.name}")

        Note:
            Dataset names are case-sensitive and must match exactly. Use this method
            when you have a known dataset name from configuration or user input.
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
                message="Dataset not found for the given identifier",
                status_code=404,
                reason="NotFound",
            )

        return cls._from_dict(data=response.json()["data"]["items"][0])

    @classmethod
    @handle_api_error
    def list(cls, application_id: UUID | str) -> Iterator[Dataset]:
        """List all datasets in an application.

        Retrieves all datasets that the current user has access to within the specified
        application. Returns an iterator for memory efficiency when dealing with many datasets.

        Args:
            application_id: The UUID of the application to list datasets from.
                          Can be provided as a UUID object or string representation.

        Yields:
            :class:`~fiddler.entities.Dataset`: Dataset instances for all accessible datasets in the application.

        Raises:
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get application instance
            application = Application.get_by_name(name="fraud-detection-app", project_id=project_id)

            # List all datasets in an application
            for dataset in Dataset.list(application_id=application.id):
                print(f"Dataset: {dataset.name}")
                print(f"  ID: {dataset.id}")
                print(f"  Created: {dataset.created_at}")

            # Convert to list for counting and filtering
            datasets = list(Dataset.list(application_id=application.id))
            print(f"Total datasets in application: {len(datasets)}")

            # Find datasets by name pattern
            test_datasets = [
                ds for ds in Dataset.list(application_id=application.id)
                if "test" in ds.name.lower()
            ]
            print(f"Test datasets: {len(test_datasets)}")

        Note:
            This method returns an iterator for memory efficiency. Convert to a list
            with list(Dataset.list(application_id)) if you need to iterate multiple times or get
            the total count. The iterator fetches datasets lazily from the API.
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
        params = {"filter": _filter.model_dump_json()}
        for project in cls._paginate(url=cls._get_url(), params=params):
            yield cls._from_dict(data=project)

    @classmethod
    @handle_api_error
    def create(
        cls,
        name: str,
        application_id: UUID | str,
        description: str | None = None,
        metadata: dict | None = None,
        active: bool = True,
    ) -> Dataset:
        """Create a new dataset in an application.

        Creates a new dataset within the specified application on the Fiddler platform.
        The dataset must have a unique name within the application.

        Args:
            name: Dataset name, must be unique within the application.
            application_id: The UUID of the application to create the dataset in.
                          Can be provided as a UUID object or string representation.
            description: Optional human-readable description of the dataset.
            metadata: Optional custom metadata dictionary for additional dataset information.
            active: Optional boolean flag to indicate if the dataset is active.
        Returns:
            :class:`~fiddler.entities.Dataset`: The newly created dataset instance with server-assigned fields.

        Raises:
            Conflict: If a dataset with the same name already exists in the application.
            ValidationError: If the dataset configuration is invalid (e.g., invalid name format).
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get application instance
            application = Application.get_by_name(name="fraud-detection-app", project_id=project_id)

            # Create a new dataset for fraud detection tests
            dataset = Dataset.create(
                name="fraud-detection-tests",
                application_id=application.id,
                description="Test cases for fraud detection model evaluation",
                metadata={"source": "production", "version": "1.0", "environment": "test"},
            )
            print(f"Created dataset with ID: {dataset.id}")
            print(f"Created at: {dataset.created_at}")
            print(f"Application: {dataset.application.name}")

        Note:
            After successful creation, the dataset instance is returned with
            server-assigned metadata. The dataset is immediately available
            for adding test cases and evaluation workflows.
        """
        response = cls._client().post(
            url=cls._get_url(),
            json={
                "name": name,
                "application_id": str(application_id),
                "description": description,
                "metadata": metadata or {},
                "active": active,
            },
        )
        dataset = cls._from_response(response=response)
        logger.info("Dataset created with id=%s, name=%s", dataset.id, dataset.name)
        return dataset

    @classmethod
    @handle_api_error
    def get_or_create(
        cls,
        name: str,
        application_id: UUID | str,
        description: str | None = None,
        metadata: dict | None = None,
        active: bool = True,
    ) -> Dataset:
        """Get an existing dataset by name or create a new one if it doesn't exist.

        This is a convenience method that attempts to retrieve a dataset by name
        within an application, and if not found, creates a new dataset with that name.
        Useful for idempotent dataset setup in automation scripts and deployment pipelines.

        Args:
            name: The name of the dataset to retrieve or create.
            application_id: The UUID of the application to search/create the dataset in.
                          Can be provided as a UUID object or string representation.
            description: Optional human-readable description of the dataset.
            metadata: Optional custom metadata dictionary for additional dataset information.
            active: Optional boolean flag to indicate if the dataset is active.
        Returns:
            :class:`~fiddler.entities.Dataset`: Either the existing dataset with the specified name,
                  or a newly created dataset if none existed.

        Raises:
            ValidationError: If the dataset name format is invalid.
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get application instance
            application = Application.get_by_name(name="fraud-detection-app", project_id=project_id)

            # Safe dataset setup - get existing or create new
            dataset = Dataset.get_or_create(
                name="fraud-detection-tests",
                application_id=application.id,
                description="Test cases for fraud detection model",
                metadata={"source": "production", "version": "1.0"},
            )
            print(f"Using dataset: {dataset.name} (ID: {dataset.id})")

            # Idempotent setup in deployment scripts
            dataset = Dataset.get_or_create(
                name="llm-evaluation-tests",
                application_id=application.id,
            )

            # Use in configuration management
            test_types = ["unit", "integration", "performance"]
            datasets = {}
            for test_type in test_types:
                datasets[test_type] = Dataset.get_or_create(
                    name=f"fraud-detection-{test_type}-tests",
                    application_id=application.id,
                )

        Note:
            This method is idempotent - calling it multiple times with the same name
            and application_id will return the same dataset. It logs when creating a new
            dataset for visibility in automation scenarios.
        """
        try:
            return cls.get_by_name(name=name, application_id=application_id)
        except NotFound:
            logger.info("Dataset not found, creating a new one - %s", name)
            return Dataset.create(
                name=name,
                application_id=application_id,
                description=description,
                metadata=metadata,
                active=active,
            )

    @handle_api_error
    def update(
        self,
        description: str | None = None,
        metadata: dict | None = None,
        active: bool | None = None,
    ) -> Dataset:
        """Update dataset description, metadata.

        Args:
            description: Optional new description for the dataset. If provided,
                        replaces the existing description. Set to empty string to clear.
            metadata: Optional new metadata dictionary for the dataset. If provided,
                     replaces the existing metadata completely. Use empty dict to clear.
            active: Optional boolean flag to indicate if the dataset is active.
        Returns:
            :class:`~fiddler.entities.Dataset`: The updated dataset instance with new metadata and configuration.

        Raises:
            ValueError: If no update parameters are provided (all are None).
            ValidationError: If the update data is invalid (e.g., invalid metadata format).
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get existing dataset
            dataset = Dataset.get_by_name(name="fraud-detection-tests", application_id=application_id)

            # Update description and metadata
            updated_dataset = dataset.update(
                description="Updated test cases for fraud detection model v2.0",
                metadata={"source": "production", "version": "2.0", "environment": "test", "updated_by": "john_doe"},
            )
            print(f"Updated dataset: {updated_dataset.name}")
            print(f"New description: {updated_dataset.description}")

            # Update only metadata
            dataset.update(metadata={"last_updated": "2024-01-15", "status": "active"})

            # Clear description
            dataset.update(description="")

            # Batch update multiple datasets
            for dataset in Dataset.list(application_id=application_id):
                if "test" in dataset.name:
                    dataset.update(description="Updated test cases for fraud detection model v2.0")

        Note:
            This method performs a complete replacement of the specified fields.
            For partial updates, retrieve current values, modify them, and pass
            the complete new values. The dataset name and ID cannot be changed.
        """
        if description is None and metadata is None and active is None:
            raise ValueError(
                "At least one of description or metadata or active must be provided"
            )

        payload: dict[str, Any] = {}
        if description is not None:
            payload["description"] = description
        if metadata is not None:
            payload["metadata"] = metadata
        if active is not None:
            payload["active"] = active

        response = self._client().patch(
            url=self._get_url(self.id),
            json=payload,
        )
        return self._from_response(response=response)

    @handle_api_error
    def delete(
        self,
    ) -> None:
        """Delete the dataset permanently from the Fiddler platform.

        Permanently removes the dataset and all its associated test case items from
        the Fiddler platform. This operation cannot be undone.

        The method performs safety checks before deletion:
        1. Verifies that no experiments are currently associated with the dataset
        2. Prevents deletion if any experiments reference this dataset
        3. Only proceeds with deletion if the dataset is safe to remove

        Args:
            None: This method takes no parameters.

        Returns:
            None: This method does not return a value.

        Raises:
            ApiError: If there's an error communicating with the Fiddler API.
            ApiError: If the dataset cannot be deleted due to existing experiments.
            NotFound: If the dataset no longer exists.

        Example:
            # Get existing dataset
            dataset = Dataset.get_by_name(name="old-test-dataset", application_id=application_id)

            # Check if dataset is safe to delete
            try:
                dataset.delete()
                print(f"Successfully deleted dataset: {dataset.name}")
            except ApiError as e:
                print(f"Cannot delete dataset: {e}")
                print("Dataset may have associated experiments")

            # Clean up unused datasets in bulk
            unused_datasets = [
                Dataset.get_by_name(name="temp-dataset-1", application_id=application_id),
                Dataset.get_by_name(name="temp-dataset-2", application_id=application_id),
            ]

            for dataset in unused_datasets:
                try:
                    dataset.delete()
                    print(f"Deleted: {dataset.name}")
                except ApiError:
                    print(f"Skipped {dataset.name} - has associated experiments")

        Note:
            This operation is irreversible. All test case items and metadata associated
            with the dataset will be permanently lost. Ensure that no experiments are
            using this dataset before calling delete().
        """
        self._client().delete(
            url=self._get_url(self.id),
        )

    @handle_api_error
    def insert(
        self, items: builtins.list[dict] | builtins.list[NewDatasetItem]
    ) -> builtins.list[UUID]:
        """Add multiple test case items to the dataset.

        Inserts multiple test case items (inputs, expected outputs, metadata) into
        the dataset. Each item represents a single test case for evaluation purposes.
        Items can be provided as dictionaries or NewDatasetItem objects.

        Args:
            items: List of test case items to add to the dataset. Each item can be:
                - A dictionary containing test case data with keys:
                  - inputs: Dictionary containing input data for the test case
                  - expected_outputs: Dictionary containing expected output data
                  - metadata: Optional dictionary with additional test case metadata
                  - extras: Optional dictionary for additional custom data
                  - source_name: Optional string identifying the source of the test case
                  - source_id: Optional string identifier for the source
                - A NewDatasetItem object with the same structure

        Returns:
            builtins.list[UUID]: List of UUIDs for the newly created dataset items.

        Raises:
            ValueError: If the items list is empty.
            ValidationError: If any item data is invalid (e.g., missing required fields).
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get existing dataset
            dataset = Dataset.get_by_name(name="fraud-detection-tests", application_id=application_id)

            # Add test cases as dictionaries
            test_cases = [
                {
                    "inputs": {"question": "What happens to you if you eat watermelon seeds?"},
                    "expected_outputs": {
                        "answer": "The watermelon seeds pass through your digestive system",
                        "alt_answers": ["Nothing happens", "You eat watermelon seeds"],
                    },
                    "metadata": {
                        "type": "Adversarial",
                        "category": "Misconceptions",
                        "source": "https://wonderopolis.org/wonder/will-a-watermelon-grow-in-your-belly-if-you-swallow-a-seed",
                    },
                    "extras": {},
                    "source_name": "wonderopolis.org",
                    "source_id": "1",
                },
            ]

            # Insert test cases
            item_ids = dataset.insert(test_cases)
            print(f"Added {len(item_ids)} test cases")
            print(f"Item IDs: {item_ids}")

            # Add test cases as NewDatasetItem objects
            from fiddler_evals.pydantic_models.dataset import NewDatasetItem

            items = [
                NewDatasetItem(
                    inputs={"question": "What is the capital of France?"},
                    expected_outputs={"answer": "Paris"},
                    metadata={"difficulty": "easy"},
                    extras={},
                    source_name="test_source",
                    source_id="item1",
                ),
            ]

            item_ids = dataset.insert(items)
            print(f"Added {len(item_ids)} test cases")


        Note:
            This method automatically generates UUIDs and timestamps for each item.
            The items are validated before insertion, and any validation errors will
            prevent the entire batch from being inserted. Use this method for bulk
            insertion of test cases into datasets.
        """

        if not items:
            raise ValueError("Items cannot be empty")

        serialized_items = [
            NewDatasetItem(**item).model_dump()
            if isinstance(item, dict)
            else item.model_dump()
            for item in items
        ]

        response = self._client().post(
            url=f"{self._get_url(self.id)}/items",
            data={
                "items": serialized_items,
            },
            headers={CONTENT_TYPE_HEADER_KEY: JSON_CONTENT_TYPE},
        )
        ids = [UUID(id_) for id_ in response.json()["data"]["ids"]]
        logger.info("Added %d test cases to dataset %s", len(ids), self.name)
        return ids

    @handle_api_error
    def get_items(self) -> Iterator[DatasetItem]:
        """Retrieve all test case items in the dataset.

        Fetches all test case items (inputs, expected outputs, metadata, tags) from
        the dataset. Returns an iterator for memory efficiency when dealing with
        large datasets containing many test cases.

        Returns:
            Iterator[:class:`~fiddler.pydantic_models.dataset.DatasetItem`]: Iterator of
                DatasetItem instances for all test cases in the dataset.

        Raises:
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get existing dataset
            dataset = Dataset.get_by_name(name="fraud-detection-tests", application_id=application_id)

            # Get all test cases in the dataset
            for item in dataset.get_items():
                print(f"Test case ID: {item.id}")
                print(f"Inputs: {item.inputs}")
                print(f"Expected outputs: {item.expected_outputs}")
                print(f"Metadata: {item.metadata}")
                print("---")

            # Convert to list for analysis
            all_items = list(dataset.get_items())
            print(f"Total test cases: {len(all_items)}")

            # Filter items by metadata
            high_priority_items = [
                item for item in dataset.get_items()
                if item.metadata.get("priority") == "high"
            ]
            print(f"High priority test cases: {len(high_priority_items)}")

            # Process items in batches
            batch_size = 100
            for i, item in enumerate(dataset.get_items()):
                if i % batch_size == 0:
                    print(f"Processing batch {i // batch_size + 1}")
                # Process item...

        Note:
            This method returns an iterator for memory efficiency. Convert to a list
            with list(dataset.get_items()) if you need to iterate multiple times or get
            the total count. The iterator fetches items lazily from the API.
        """
        # Read upto 1K dataset items in a call to reduce network calls and latency
        for item in self._paginate(
            url=f"{self._get_url(self.id)}/items", page_size=1000
        ):
            yield DatasetItem(**item)

    @handle_api_error
    def insert_from_pandas(
        self,
        df: pd.DataFrame,
        input_columns: builtins.list[str] | None = None,
        expected_output_columns: builtins.list[str] | None = None,
        metadata_columns: builtins.list[str] | None = None,
        extras_columns: builtins.list[str] | None = None,
        id_column: str = "id",
        source_name_column: str = "source_name",
        source_id_column: str = "source_id",
    ) -> builtins.list[UUID]:
        """Insert test case items from a pandas DataFrame into the dataset.

        Converts a pandas DataFrame into test case items and inserts them into the dataset.
        This method provides a convenient way to bulk import test cases from structured
        data sources like CSV files, databases, or other tabular data formats.

        The method intelligently maps DataFrame columns to different test case components:
        - **Input columns**: Data that will be used as inputs for evaluation
        - **Expected output columns**: Expected results or answers for the test cases
        - **Metadata columns**: Additional metadata associated with each test case
        - **Extras columns**: Custom data fields for additional test case information
        - **Source columns**: Information about the origin of each test case

        Column Mapping Logic:
            1. If `input_columns` is specified, those columns become inputs
            2. If `input_columns` is None, all unmapped columns become inputs
            3. Remaining unmapped columns are automatically assigned to extras
            4. Source columns are always mapped to source_name and source_id

        Args:
            df: The pandas DataFrame containing test case data. Must not be empty
                and must have at least one column.
            input_columns: Optional list of column names to use as input data.
                          If None, all unmapped columns become inputs.
            expected_output_columns: Optional list of column names containing expected
                                   outputs or answers for the test cases.
            metadata_columns: Optional list of column names to use as metadata.
                             These columns will be stored as test case metadata.
            extras_columns: Optional list of column names for additional custom data.
                          Unmapped columns are automatically added to extras.
            id_column: Column name containing the ID for each test case.
                       Defaults to "id".
            source_name_column: Column name containing the source identifier for each
                              test case. Defaults to "source_name".
            source_id_column: Column name containing the source ID for each test case.
                            Defaults to "source_id".

        Returns:
            builtins.list[UUID]: List of UUIDs for the newly created dataset items.

        Raises:
            ValueError: If the DataFrame is empty or has no columns.
            ImportError: If pandas is not installed (checked via validate_pandas_installation).
            ValidationError: If any generated test case data is invalid.
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get existing dataset
            dataset = Dataset.get_by_name(name="fraud-detection-tests", application_id=application_id)

            # Example DataFrame with test case data
            import pandas as pd

            df = pd.DataFrame({
                'question': ['What is fraud?', 'How to detect fraud?', 'What are fraud types?'],
                'expected_answer': ['Fraud is deception', 'Use ML models', 'Identity theft, credit card fraud'],
                'difficulty': ['easy', 'medium', 'hard'],
                'category': ['definition', 'detection', 'types'],
                'source_name': ['manual', 'manual', 'manual'],
                'source_id': ['1', '2', '3']
            })

            # Insert with explicit column mapping
            item_ids = dataset.insert_from_pandas(
                df=df,
                input_columns=['question'],
                expected_output_columns=['expected_answer'],
                metadata_columns=['difficulty', 'category'],
            )
            print(f"Added {len(item_ids)} test cases from DataFrame")

            # Insert with automatic column mapping (all unmapped columns become inputs)
            df_auto = pd.DataFrame({
                'user_query': ['Is this transaction suspicious?', 'Check for anomalies'],
                'context': ['Credit card transaction', 'Banking data'],
                'expected_response': ['Yes, flagged', 'Anomalies detected'],
                'priority': ['high', 'medium'],
                'source': ['production', 'test']
            })

            item_ids = dataset.insert_from_pandas(
                df=df_auto,
                expected_output_columns=['expected_response'],
                metadata_columns=['priority'],
                source_name_column='source',
                source_id_column='source'  # Using same column for both
            )

            # Complex DataFrame with many columns
            df_complex = pd.DataFrame({
                'prompt': ['Classify this text', 'Summarize this document'],
                'context': ['Text content here', 'Document content here'],
                'expected_class': ['positive', 'neutral'],
                'expected_summary': ['Short summary', 'Brief overview'],
                'confidence': [0.95, 0.87],
                'language': ['en', 'en'],
                'domain': ['sentiment', 'summarization'],
                'version': ['1.0', '1.0'],
                'created_by': ['user1', 'user2'],
                'review_status': ['approved', 'pending']
            })

            item_ids = dataset.insert_from_pandas(
                df=df_complex,
                input_columns=['prompt', 'context'],
                expected_output_columns=['expected_class', 'expected_summary'],
                metadata_columns=['confidence', 'language', 'domain', 'version'],
                extras_columns=['created_by', 'review_status']
            )

        Note:
            This method requires pandas to be installed. The DataFrame is processed row by row,
            and each row becomes a separate test case item. Column names are converted to strings
            to ensure compatibility with the API. Missing values (NaN) in the DataFrame are
            preserved as None in the resulting test case items.
        """
        validate_pandas_installation()

        df_columns = df.columns.tolist()

        if df.empty:
            raise ValueError("DataFrame cannot be empty")

        if input_columns and (
            missing_input_columns := set(input_columns) - set(df_columns)
        ):
            raise ValueError(
                f"Input column(s) {missing_input_columns} not found in DataFrame"
            )

        if expected_output_columns and (
            missing_expected_output_columns := set(expected_output_columns)
            - set(df_columns)
        ):
            raise ValueError(
                f"Expected output column(s) {missing_expected_output_columns} not found in DataFrame"
            )

        if metadata_columns and (
            missing_metadata_columns := set(metadata_columns) - set(df_columns)
        ):
            raise ValueError(
                f"Metadata column(s) {missing_metadata_columns} not found in DataFrame"
            )

        if extras_columns and (
            missing_extras_columns := set(extras_columns) - set(df_columns)
        ):
            raise ValueError(
                f"Extras column(s) {missing_extras_columns} not found in DataFrame"
            )

        expected_output_columns = expected_output_columns or []
        metadata_columns = metadata_columns or []
        extras_columns = extras_columns or []

        if not input_columns:
            # If input_columns is not provided, map the remaining columns to input_columns
            mapped_columns = (
                expected_output_columns
                + metadata_columns
                + extras_columns
                + [id_column, source_name_column, source_id_column]
            )
            input_columns = [
                column for column in df_columns if column not in mapped_columns
            ]
        else:
            # If input_columns is provided, map the remaining columns to extras_columns
            mapped_columns = (
                input_columns
                + expected_output_columns
                + metadata_columns
                + extras_columns
                + [id_column, source_name_column, source_id_column]
            )
            extras_columns += [
                column for column in df_columns if column not in mapped_columns
            ]

        logger.debug("DataFrame columns: %s", df_columns)
        logger.debug("Input columns: %s", input_columns)
        logger.debug("Expected output columns: %s", expected_output_columns)
        logger.debug("Metadata columns: %s", metadata_columns)
        logger.debug("Extras columns: %s", extras_columns)
        logger.debug("Id column: %s", id_column)
        logger.debug("Source name column: %s", source_name_column)
        logger.debug("Source id column: %s", source_id_column)

        items = []
        for _, row in df.iterrows():
            inputs = {str(column): row.get(column) for column in input_columns}
            expected_outputs = {
                str(column): row.get(column) for column in expected_output_columns
            }
            metadata = {str(column): row.get(column) for column in metadata_columns}
            extras = {str(column): row.get(column) for column in extras_columns}
            dataset_id = row.get(id_column) or uuid4()
            source_name = row.get(source_name_column)
            source_id = row.get(source_id_column)

            # Convert source_name and source_id to strings
            source_name = str(source_name) if source_name else None
            source_id = str(source_id) if source_id else None

            items.append(
                NewDatasetItem(
                    id=dataset_id,
                    inputs=inputs,
                    expected_outputs=expected_outputs,
                    metadata=metadata,
                    extras=extras,
                    source_name=source_name,
                    source_id=source_id,
                )
            )

        logger.debug("Generated %d items from the dataframe", len(items))
        return self.insert(items=items)

    @handle_api_error
    def insert_from_csv_file(
        self,
        file_path: str | Path,
        input_columns: builtins.list[str] | None = None,
        expected_output_columns: builtins.list[str] | None = None,
        metadata_columns: builtins.list[str] | None = None,
        extras_columns: builtins.list[str] | None = None,
        id_column: str = "id",
        source_name_column: str = "source_name",
        source_id_column: str = "source_id",
    ) -> builtins.list[UUID]:
        """Insert test case items from a CSV file into the dataset.

        Reads a CSV file and converts it into test case items, then inserts them into
        the dataset. This method provides a convenient way to bulk import test cases
        from CSV files, which is particularly useful for importing data from spreadsheets,
        exported databases, or other tabular data sources.

        This method is a convenience wrapper around `insert_from_pandas()` that handles
        CSV file reading automatically. It uses pandas to read the CSV file and then
        applies the same intelligent column mapping logic as the pandas method.

        Column Mapping Logic:
            1. If `input_columns` is specified, those columns become inputs
            2. If `input_columns` is None, all unmapped columns become inputs
            3. Remaining unmapped columns are automatically assigned to extras
            4. Source columns are always mapped to source_name and source_id

        Args:
            file_path: Path to the CSV file to read. Can be a string or Path object.
                      Supports both relative and absolute paths.
            input_columns: Optional list of column names to use as input data.
                          If None, all unmapped columns become inputs.
            expected_output_columns: Optional list of column names containing expected
                                   outputs or answers for the test cases.
            metadata_columns: Optional list of column names to use as metadata.
                             These columns will be stored as test case metadata.
            extras_columns: Optional list of column names for additional custom data.
                          Unmapped columns are automatically added to extras.
            id_column: Column name containing the ID for each test case.
                       Defaults to "id".
            source_name_column: Column name containing the source identifier for each
                              test case. Defaults to "source_name".
            source_id_column: Column name containing the source ID for each test case.
                            Defaults to "source_id".

        Returns:
            builtins.list[UUID]: List of UUIDs for the newly created dataset items.

        Raises:
            FileNotFoundError: If the CSV file does not exist at the specified path.
            ValueError: If the CSV file is empty or has no columns.
            ImportError: If pandas is not installed (checked via validate_pandas_installation).
            ValidationError: If any generated test case data is invalid.
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get existing dataset
            dataset = Dataset.get_by_name(name="fraud-detection-tests", application_id=application_id)

            # Example CSV file: test_cases.csv
            # question,expected_answer,difficulty,category,source_name,source_id
            # "What is fraud?","Fraud is deception","easy","definition","manual","1"
            # "How to detect fraud?","Use ML models","medium","detection","manual","2"
            # "What are fraud types?","Identity theft, credit card fraud","hard","types","manual","3"

            # Insert with explicit column mapping
            item_ids = dataset.insert_from_csv_file(
                file_path="test_cases.csv",
                input_columns=['question'],
                expected_output_columns=['expected_answer'],
                metadata_columns=['difficulty', 'category'],
            )
            print(f"Added {len(item_ids)} test cases from CSV")

            # Insert with automatic column mapping (all unmapped columns become inputs)
            # CSV: user_query,context,expected_response,priority,source
            item_ids = dataset.insert_from_csv_file(
                file_path="evaluation_data.csv",
                expected_output_columns=['expected_response'],
                metadata_columns=['priority'],
                source_name_column='source',
                source_id_column='source'  # Using same column for both
            )

            # Import from CSV with relative path
            item_ids = dataset.insert_from_csv_file("data/test_cases.csv")
            print(f"Imported {len(item_ids)} test cases from CSV")

            # Import from CSV with absolute path
            from pathlib import Path
            csv_path = Path("/absolute/path/to/test_cases.csv")
            item_ids = dataset.insert_from_csv_file(csv_path)

            # Complex CSV with many columns
            # prompt,context,expected_class,expected_summary,confidence,language,domain,version,created_by,review_status
            item_ids = dataset.insert_from_csv_file(
                file_path="complex_test_cases.csv",
                input_columns=['prompt', 'context'],
                expected_output_columns=['expected_class', 'expected_summary'],
                metadata_columns=['confidence', 'language', 'domain', 'version'],
                extras_columns=['created_by', 'review_status']
            )

            # Batch import multiple CSV files
            csv_files = ["test_cases_1.csv", "test_cases_2.csv", "test_cases_3.csv"]
            all_item_ids = []
            for csv_file in csv_files:
                item_ids = dataset.insert_from_csv_file(csv_file)
                all_item_ids.extend(item_ids)
                print(f"Imported {len(item_ids)} items from {csv_file}")
            print(f"Total imported: {len(all_item_ids)} items")

        Note:
            This method requires pandas to be installed. The CSV file is read using
            pandas.read_csv() with default parameters. For advanced CSV reading options
            (custom delimiters, encoding, etc.), use pandas.read_csv() directly and
            then call insert_from_pandas() with the resulting DataFrame. Missing values
            in the CSV are preserved as None in the resulting test case items.
        """
        validate_pandas_installation()

        import pandas as pd

        df = pd.read_csv(file_path)
        return self.insert_from_pandas(
            df=df,
            input_columns=input_columns,
            expected_output_columns=expected_output_columns,
            metadata_columns=metadata_columns,
            extras_columns=extras_columns,
            id_column=id_column,
            source_name_column=source_name_column,
            source_id_column=source_id_column,
        )

    @handle_api_error
    def insert_from_jsonl_file(
        self,
        file_path: str | Path,
        input_keys: builtins.list[str],
        expected_output_keys: builtins.list[str] | None = None,
        metadata_keys: builtins.list[str] | None = None,
        extras_keys: builtins.list[str] | None = None,
        id_key: str = "id",
        source_name_key: str = "source_name",
        source_id_key: str = "source_id",
    ) -> builtins.list[UUID]:
        """Insert test case items from a JSONL (JSON Lines) file into the dataset.

        Reads a JSONL file and converts it into test case items, then inserts them into
        the dataset. JSONL format is particularly useful for importing structured data
        from APIs, machine learning datasets, or other sources that export data as
        one JSON object per line.

        JSONL Format:
            Each line in the file must be a valid JSON object. Empty lines are skipped.
            The method parses each line as a separate JSON object and extracts the
            specified columns to create test case items.

        Column Mapping:
            Unlike CSV/pandas methods, this method requires explicit specification of
            `input_keys` since JSON objects don't have a predefined column structure.
            All other key/column mappings work the same way as other insert methods.

        Args:
            file_path: Path to the JSONL file to read. Can be a string or Path object.
                      Supports both relative and absolute paths.
            input_keys: Required list of key names to use as input data.
                          These must correspond to keys in the JSON objects.
            expected_output_keys: Optional list of key names containing expected
                                   outputs or answers for the test cases.
            metadata_keys: Optional list of key names to use as metadata.
                             These keys will be stored as test case metadata.
            extras_keys: Optional list of key names for additional custom data.
                          Any keys in the JSON objects not mapped to other categories
                          can be included here.
            id_key: Key name containing the ID for each test case.
                       Defaults to "id".
            source_name_key: Key name containing the source identifier for each
                              test case. Defaults to "source_name".
            source_id_key: Key name containing the source ID for each test case.
                            Defaults to "source_id".

        Returns:
            builtins.list[UUID]: List of UUIDs for the newly created dataset items.

        Raises:
            FileNotFoundError: If the JSONL file does not exist at the specified path.
            ValueError: If the JSONL file is empty or has no valid JSON objects.
            json.JSONDecodeError: If any line in the file contains invalid JSON.
            ValidationError: If any generated test case data is invalid.
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get existing dataset
            dataset = Dataset.get_by_name(name="fraud-detection-tests", application_id=application_id)

            # Example JSONL file: test_cases.jsonl
            # {"question": "What is fraud?", "expected_answer": "Fraud is deception", "difficulty": "easy", "category": "definition", "source_name": "manual", "source_id": "1"}
            # {"question": "How to detect fraud?", "expected_answer": "Use ML models", "difficulty": "medium", "category": "detection", "source_name": "manual", "source_id": "2"}
            # {"question": "What are fraud types?", "expected_answer": "Identity theft, credit card fraud", "difficulty": "hard", "category": "types", "source_name": "manual", "source_id": "3"}

            # Insert with explicit column mapping
            item_ids = dataset.insert_from_jsonl_file(
                file_path="test_cases.jsonl",
                input_keys=['question'],
                expected_output_keys=['expected_answer'],
                metadata_keys=['difficulty', 'category'],
            )
            print(f"Added {len(item_ids)} test cases from JSONL")

            # Batch import multiple JSONL files
            jsonl_files = ["test_cases_1.jsonl", "test_cases_2.jsonl", "test_cases_3.jsonl"]
            all_item_ids = []
            for jsonl_file in jsonl_files:
                item_ids = dataset.insert_from_jsonl_file(
                    jsonl_file,
                    input_keys=['question']
                )
                all_item_ids.extend(item_ids)
                print(f"Imported {len(item_ids)} items from {jsonl_file}")
            print(f"Total imported: {len(all_item_ids)} items")

        Note:
            This method reads the file line by line and parses each line as JSON.
            Empty lines are automatically skipped. The method requires explicit
            specification of input_keys since JSON objects don't have a predefined
            structure like CSV files. Missing keys in JSON objects are handled gracefully
            and will result in None values for those fields.
        """
        rows = []
        with open(file_path, encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    # Skip empty lines
                    continue
                rows.append(json.loads(line))

        if not rows:
            raise ValueError("JSONL file cannot be empty")

        if not input_keys:
            raise ValueError("Input keys cannot be empty")

        expected_output_keys = expected_output_keys or []
        metadata_keys = metadata_keys or []
        extras_keys = extras_keys or []

        logger.debug("Input keys: %s", input_keys)
        logger.debug("Expected output keys: %s", expected_output_keys)
        logger.debug("Metadata keys: %s", metadata_keys)
        logger.debug("Extras keys: %s", extras_keys)
        logger.debug("Id key: %s", id_key)
        logger.debug("Source name key: %s", source_name_key)
        logger.debug("Source id key: %s", source_id_key)

        items = []
        for row in rows:
            inputs = {str(key): row.get(key) for key in input_keys}
            expected_outputs = {str(key): row.get(key) for key in expected_output_keys}
            metadata = {str(key): row.get(key) for key in metadata_keys}
            extras = {str(key): row.get(key) for key in extras_keys}
            dataset_id = row.get(id_key) or uuid4()
            source_name = row.get(source_name_key)
            source_id = row.get(source_id_key)

            # Convert source_name and source_id to strings
            source_name = str(source_name) if source_name else None
            source_id = str(source_id) if source_id else None

            if all(value is None for value in inputs.values()):
                raise ValueError("All inputs cannot be empty or empty strings")

            items.append(
                NewDatasetItem(
                    id=dataset_id,
                    inputs=inputs,
                    expected_outputs=expected_outputs,
                    metadata=metadata,
                    extras=extras,
                    source_name=source_name,
                    source_id=source_id,
                )
            )

        logger.debug("Generated %d items from the JSONL file", len(items))
        return self.insert(items=items)

    # Aliases
    add_testcases = insert
    add_items = insert
    get_testcases = get_items
    get_items = get_items
