"""
Project entity for organizing and managing GenAI Apps in Fiddler.

The Project class represents a logical container for organizing related GenAI Applications,
evaluation datasets, experiments and monitoring configurations. Projects provide isolation,
access control, and organizational structure for LLM/GenAI Apps offline and online monitoring workflows.

Key Concepts:
    - **Organization**: Projects group related GenAI Apps and resources together
    - **Isolation**: Each project maintains separate namespaces for GenAI Apps and data
    - **Access Control**: Projects can have different permissions and access levels
    - **Lifecycle Management**: Projects coordinate the lifecycle of contained resources

Common Workflow:
    1. Create or retrieve a project for your LLM/GenAI use case
    2. Add an application to the project using Application.create()
    3. Evaluate your LLM/Agent/App using evaluate()
    4. Manage project-level settings and access permissions

Example:
    # Create a new project
    project = Project.create(name="fraud_detection")

Note:
    Project names must be unique within an organization and follow slug-like naming
    conventions (lowercase, hyphens, underscores allowed). Projects cannot be renamed
    after creation, but can be deleted if no longer needed.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator
from uuid import UUID

from fiddler_evals.decorators import handle_api_error
from fiddler_evals.entities.base import BaseEntity
from fiddler_evals.exceptions import NotFound
from fiddler_evals.pydantic_models.filter_query import (
    OperatorType,
    QueryCondition,
    QueryRule,
)
from fiddler_evals.pydantic_models.project import ProjectResponse

logger = logging.getLogger(__name__)

ASSET_TYPE = "GEN_AI_APP"


@dataclass
class Project(BaseEntity):
    """Represents a project container for organizing GenAI Apps and resources.

    A Project is the top-level organizational unit in Fiddler that groups related
    GenAI Applications, datasets, and monitoring configurations. Projects provide
    logical separation, access control, and resource management for GenAI App monitoring workflows.

    Key Features:
        - **GenAI Apps Organization**: Container for related GenAI apps
        - **Resource Isolation**: Separate namespaces prevent naming conflicts
        - **Access Management**: Project-level permissions and access control
        - **Monitoring Coordination**: Centralized monitoring and alerting configuration
        - **Lifecycle Management**: Coordinated creation, updates, and deletion of resources

    Project Lifecycle:
        1. **Creation**: Create project with unique name within organization
        2. **App creation**: Create GenAI applications with Application().create()
        3. **Configuration**: Set up monitoring, alerts, and evaluators.
        4. **Operations**: Publish logs, monitor performance, manage alerts
        5. **Maintenance**: Update configurations
        6. **Cleanup**: Delete project when no longer needed (removes all contained resources)

    Attributes:
        name (str): Project name, must be unique within the organization.
                   Should follow slug-like naming (lowercase, hyphens, underscores).
        id (UUID, optional): Unique project identifier, assigned by server on creation.
        created_at (datetime, optional): Project creation timestamp.
        updated_at (datetime, optional): Last modification timestamp.

    Example:
        # Create a new project for fraud detection models
        project = Project.create(name="fraud-detection-2024")
        print(f"Created project: {project.name} (ID: {project.id})")

    Note:
        Projects are permanent containers - once created, the name cannot be changed.
        Deleting a project removes all contained models, datasets, and configurations.
        Consider the organizational structure carefully before creating projects.
    """

    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def _get_url(id_: UUID | str | None = None) -> str:
        """Get project resource/item URL.

        Constructs the appropriate API endpoint URL for project operations.
        """
        url = "/v3/projects"
        return url if not id_ else f"{url}/{id_}"

    @classmethod
    def _from_dict(cls, data: dict) -> Project:
        """Build the entity object from the given dictionary.

        Creates a Project instance from a dictionary containing project data,
        typically from an API response. This method handles deserialization and
        validation of all project fields.
        """

        # Deserialize the response
        response_obj = ProjectResponse(**data)

        # Initialize
        instance = cls(
            id=response_obj.id,
            name=response_obj.name,
            created_at=response_obj.created_at,
            updated_at=response_obj.updated_at,
        )

        return instance

    @classmethod
    @handle_api_error
    def get_by_id(cls, id_: UUID | str) -> Project:
        """Retrieve a project by its unique identifier.

        Fetches a project from the Fiddler platform using its UUID. This is the most
        direct way to retrieve a project when you know its ID.

        Args:
            id_: The unique identifier (UUID) of the project to retrieve.
                Can be provided as a UUID object or string representation.

        Returns:
            :class:`~fiddler.entities.Project`: The project instance with all metadata and configuration.

        Raises:
            NotFound: If no project exists with the specified ID.
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get project by UUID
            project = Project.get_by_id(id_="550e8400-e29b-41d4-a716-446655440000")
            print(f"Retrieved project: {project.name}")
            print(f"Created: {project.created_at}")

        Note:
            This method makes an API call to fetch the latest project state from the server.
            The returned project instance reflects the current state in Fiddler.
        """
        response = cls._client().get(url=cls._get_url(id_))
        return cls._from_response(response=response)

    @classmethod
    @handle_api_error
    def get_by_name(cls, name: str) -> Project:
        """Retrieve a project by name.

        Finds and returns a project using its name within the organization. This is useful
        when you know the project name but not its UUID. Project names are unique within
        an organization, making this a reliable lookup method.

        Args:
            name: The name of the project to retrieve. Project names are unique
                 within an organization and are case-sensitive.

        Returns:
            :class:`~fiddler.entities.Project`: The project instance matching the specified name.

        Raises:
            NotFound: If no project exists with the specified name in the organization.
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get project by name
            project = Project.get_by_name(name="fraud-detection")
            print(f"Found project: {project.name} (ID: {project.id})")
            print(f"Created: {project.created_at}")

            # Get project for specific environment
            prod_project = Project.get_by_name(name="fraud-detection-prod")
            staging_project = Project.get_by_name(name="fraud-detection-staging")

        Note:
            Project names are case-sensitive and must match exactly. Use this method
            when you have a known project name from configuration or user input.
        """
        _filter = QueryCondition(
            rules=[
                QueryRule(field="name", operator=OperatorType.EQUAL, value=name),
                QueryRule(
                    field="asset_type", operator=OperatorType.EQUAL, value=ASSET_TYPE
                ),
            ]
        )

        response = cls._client().get(
            url=cls._get_url(), params={"filter": _filter.model_dump_json()}
        )
        if response.json()["data"]["total"] == 0:
            raise NotFound(
                message="Project not found for the given identifier",
                status_code=404,
                reason="NotFound",
            )

        return cls._from_dict(data=response.json()["data"]["items"][0])

    @classmethod
    @handle_api_error
    def list(cls) -> Iterator[Project]:
        """List all projects in the organization.

        Retrieves all projects that the current user has access to within the organization.
        Returns an iterator for memory efficiency when dealing with many projects.

        Yields:
            :class:`~fiddler.entities.Project`: Project instances for all accessible projects.

        Raises:
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # List all projects
            for project in Project.list():
                print(f"Project: {project.name}")
                print(f"  ID: {project.id}")
                print(f"  Created: {project.created_at}")

            # Convert to list for counting and filtering
            projects = list(Project.list())
            print(f"Total accessible projects: {len(projects)}")

            # Find projects by name pattern
            prod_projects = [
                p for p in Project.list()
                if "prod" in p.name.lower()
            ]
            print(f"Production projects: {len(prod_projects)}")

            # Get project summaries
            for project in Project.list():
                print(f"{project.name}")

        Note:
            This method returns an iterator for memory efficiency. Convert to a list
            with list(Project.list()) if you need to iterate multiple times or get
            the total count. The iterator fetches projects lazily from the API.
        """
        _filter = QueryCondition(
            rules=[
                QueryRule(
                    field="asset_type", operator=OperatorType.EQUAL, value=ASSET_TYPE
                ),
            ]
        )
        params = {"filter": _filter.model_dump_json()}
        for project in cls._paginate(url=cls._get_url(), params=params):
            yield cls._from_dict(data=project)

    @classmethod
    @handle_api_error
    def create(cls, name: str) -> Project:
        """Create the project on the Fiddler platform.

        Persists this project instance to the Fiddler platform, making it available
        for adding GenAI Apps, configuring monitoring, and other operations. The project
        must have a unique name within the organization.

        Args:
            name: Project name, must be unique within the organization.
                 Should follow slug-like naming conventions:
                 - Use lowercase letters, numbers, hyphens, and underscores
                 - Start with a letter or number

        Returns:
            :class:`~fiddler.entities.Project`: This project instance, updated with server-assigned fields like
                  ID, creation timestamp, and other metadata.

        Raises:
            Conflict: If a project with the same name already exists in the organization.
            ValidationError: If the project configuration is invalid (e.g., invalid name format).
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Create a new project
            project = Project.create(name="customer-churn-analysis")
            print(f"Created project with ID: {project.id}")
            print(f"Created at: {project.created_at}")

            # Project is now available for adding GenAI Apps
            assert project.id is not None

        Note:
            After successful creation, the project instance is returned with
            server-assigned metadata. The project is immediately available
            for adding GenAI Apps and other resources.
        """
        response = cls._client().post(
            url=cls._get_url(),
            json={
                "name": name,
                "asset_type": "GEN_AI_APP",
            },
        )
        project = cls._from_response(response=response)
        logger.info("Project created with id=%s, name=%s", project.id, project.name)
        return project

    @classmethod
    @handle_api_error
    def get_or_create(cls, name: str) -> Project:
        """Get an existing project by name or create a new one if it doesn't exist.

        This is a convenience method that attempts to retrieve a project by name,
        and if not found, creates a new project with that name. Useful for idempotent
        project setup in automation scripts and deployment pipelines.

        Args:
            name: The name of the project to retrieve or create. Must follow
                 project naming conventions (slug-like format).

        Returns:
            :class:`~fiddler.entities.Project`: Either the existing project with the specified name,
                  or a newly created project if none existed.

        Raises:
            ValidationError: If the project name format is invalid.
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Safe project setup - get existing or create new
            project = Project.get_or_create(name="fraud-detection-prod")
            print(f"Using project: {project.name} (ID: {project.id})")

            # Idempotent setup in deployment scripts
            project = Project.get_or_create(name="llm-pipeline-staging")

            # Use in configuration management
            environments = ["dev", "staging", "prod"]
            projects = {}
            for env in environments:
                projects[env] = Project.get_or_create(name=f"fraud-detection-{env}")

        Note:
            This method is idempotent - calling it multiple times with the same name
            will return the same project. It logs when creating a new project for
            visibility in automation scenarios.
        """
        try:
            return cls.get_by_name(name=name)
        except NotFound:
            logger.info("Project not found, creating a new one - %s", name)
            return Project.create(name=name)
