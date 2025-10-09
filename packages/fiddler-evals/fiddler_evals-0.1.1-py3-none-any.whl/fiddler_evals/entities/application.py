"""
GenAI Application entity for organizing and managing GenAI application resources in Fiddler.

The Application class represents a logical container for organizing related GenAI application
resources including datasets, experiments, evaluators, and monitoring configurations. Applications
provide isolation, access control, and organizational structure for GenAI App monitoring workflows
within a project context.

Key Concepts:
    - **Project Container**: Applications are contained within projects and inherit project-level settings
    - **Resource Organization**: Applications group related GenAI resources and configurations
    - **Access Control**: Applications can have different permissions and access levels within projects
    - **Lifecycle Management**: Applications coordinate the lifecycle of contained resources

Common Workflow:
    1. Create or retrieve a project for your GenAI use case
    2. Create applications within the project using Application.create()
    3. Add datasets, evaluators, and monitoring configurations to the application
    4. Manage application-level settings and access permissions

Example:
    # Create a new application within a project
    application = Application.create(name="fraud_detection_app", project_id=project_id)

Note:
    Application names must be unique within a project. Applications cannot be renamed
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
from fiddler_evals.pydantic_models.application import ApplicationResponse
from fiddler_evals.pydantic_models.compact import ProjectCompact, UserCompact
from fiddler_evals.pydantic_models.filter_query import (
    OperatorType,
    QueryCondition,
    QueryRule,
)

logger = logging.getLogger(__name__)


@dataclass
class Application(BaseEntity):
    """Represents a GenAI Application container for organizing GenAI application resources.

    An Application is a logical container within a Project that groups related GenAI
    application resources including datasets, experiments, evaluators, and monitoring
    configurations. Applications provide resource organization, access control, and
    lifecycle management for GenAI App monitoring workflows.

    Key Features:
        - **Resource Organization**: Container for related GenAI application resources
        - **Project Context**: Applications are scoped within projects for isolation
        - **Access Management**: Application-level permissions and access control
        - **Monitoring Coordination**: Centralized monitoring and alerting configuration
        - **Lifecycle Management**: Coordinated creation, updates, and deletion of resources

    Application Lifecycle:
        1. **Creation**: Create application with unique name within a project
        2. **Configuration**: Set up datasets, evaluators, and monitoring
        3. **Operations**: Publish logs, monitor performance, manage alerts
        4. **Maintenance**: Update configurations and resources
        5. **Cleanup**: Delete application when no longer needed

    Attributes:
        id (UUID): Unique application identifier, assigned by server on creation.
        name (str): Application name, must be unique within the project.
        created_at (datetime): Application creation timestamp.
        updated_at (datetime): Last modification timestamp.
        created_by (UserCompact): User who created the application.
        updated_by (UserCompact): User who last updated the application.
        project (ProjectCompact): Project containing this application.

    Example:
        # Create a new application for fraud detection
        application = Application.create(name="fraud-detection-app", project_id=project_id)
        print(f"Created application: {application.name} (ID: {application.id})")

    Note:
        Applications are permanent containers - once created, the name cannot be changed.
        Deleting an application removes all contained resources and configurations.
        Consider the organizational structure carefully before creating applications.
    """

    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
    created_by: UserCompact
    updated_by: UserCompact
    project: ProjectCompact

    @staticmethod
    def _get_url(id_: UUID | str | None = None) -> str:
        """Get application resource/item URL.

        Constructs the appropriate API endpoint URL for application operations.
        """
        url = "/v3/applications"
        return url if not id_ else f"{url}/{id_}"

    @classmethod
    def _from_dict(cls, data: dict) -> Application:
        """Build the entity object from the given dictionary.

        Creates an Application instance from a dictionary containing application data,
        typically from an API response. This method handles deserialization and
        validation of all application fields.
        """

        # Deserialize the response
        response_obj = ApplicationResponse(**data)

        # Initialize
        instance = cls(
            id=response_obj.id,
            name=response_obj.name,
            created_at=response_obj.created_at,
            updated_at=response_obj.updated_at,
            created_by=response_obj.created_by,
            updated_by=response_obj.updated_by,
            project=response_obj.project,
        )

        return instance

    @classmethod
    @handle_api_error
    def get_by_id(cls, id_: UUID | str) -> Application:
        """Retrieve an application by its unique identifier.

        Fetches an application from the Fiddler platform using its UUID. This is the most
        direct way to retrieve an application when you know its ID.

        Args:
            id_: The unique identifier (UUID) of the application to retrieve.
                Can be provided as a UUID object or string representation.

        Returns:
            :class:`~fiddler.entities.Application`: The application instance with all metadata and configuration.

        Raises:
            NotFound: If no application exists with the specified ID.
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get application by UUID
            application = Application.get_by_id(id_="550e8400-e29b-41d4-a716-446655440000")
            print(f"Retrieved application: {application.name}")
            print(f"Created: {application.created_at}")
            print(f"Project: {application.project.name}")

        Note:
            This method makes an API call to fetch the latest application state from the server.
            The returned application instance reflects the current state in Fiddler.
        """
        response = cls._client().get(url=cls._get_url(id_))
        return cls._from_response(response=response)

    @classmethod
    @handle_api_error
    def get_by_name(cls, name: str, project_id: UUID | str) -> Application:
        """Retrieve an application by name within a project.

        Finds and returns an application using its name within the specified project.
        This is useful when you know the application name and project but not its UUID.
        Application names are unique within a project, making this a reliable lookup method.

        Args:
            name: The name of the application to retrieve. Application names are unique
                 within a project and are case-sensitive.
            project_id: The UUID of the project containing the application.
                       Can be provided as a UUID object or string representation.

        Returns:
            :class:`~fiddler.entities.Application`: The application instance matching the specified name.

        Raises:
            NotFound: If no application exists with the specified name in the project.
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get project instance
            project = Project.get_by_name(name="fraud-detection-project")

            # Get application by name within a project
            application = Application.get_by_name(
                name="fraud-detection-app",
                project_id=project.id
            )
            print(f"Found application: {application.name} (ID: {application.id})")
            print(f"Created: {application.created_at}")
            print(f"Project: {application.project.name}")

        Note:
            Application names are case-sensitive and must match exactly. Use this method
            when you have a known application name from configuration or user input.
        """
        _filter = QueryCondition(
            rules=[
                QueryRule(field="name", operator=OperatorType.EQUAL, value=name),
                QueryRule(
                    field="project_id",
                    operator=OperatorType.EQUAL,
                    value=str(project_id),
                ),
            ]
        )

        response = cls._client().get(
            url=cls._get_url(), params={"filter": _filter.model_dump_json()}
        )
        if response.json()["data"]["total"] == 0:
            raise NotFound(
                message="Application not found for the given identifier",
                status_code=404,
                reason="NotFound",
            )

        return cls._from_dict(data=response.json()["data"]["items"][0])

    @classmethod
    @handle_api_error
    def list(cls, project_id: UUID | str) -> Iterator[Application]:
        """List all applications in a project.

        Retrieves all applications that the current user has access to within the specified
        project. Returns an iterator for memory efficiency when dealing with many applications.

        Args:
            project_id: The UUID of the project to list applications from.
                       Can be provided as a UUID object or string representation.

        Yields:
            :class:`~fiddler.entities.Application`: Application instances for all accessible applications in the project.

        Raises:
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get project instance
            project = Project.get_by_name(name="fraud-detection-project")

            # List all applications in a project
            for application in Application.list(project_id=project.id):
                print(f"Application: {application.name}")
                print(f"  ID: {application.id}")
                print(f"  Created: {application.created_at}")

            # Convert to list for counting and filtering
            applications = list(Application.list(project_id=project.id))
            print(f"Total applications in project: {len(applications)}")

            # Find applications by name pattern
            fraud_apps = [
                app for app in Application.list(project_id=project.id)
                if "fraud" in app.name.lower()
            ]
            print(f"Fraud detection applications: {len(fraud_apps)}")

        Note:
            This method returns an iterator for memory efficiency. Convert to a list
            with list(Application.list(project_id)) if you need to iterate multiple times or get
            the total count. The iterator fetches applications lazily from the API.
        """
        _filter = QueryCondition(
            rules=[
                QueryRule(
                    field="project_id",
                    operator=OperatorType.EQUAL,
                    value=str(project_id),
                ),
            ]
        )
        params = {"filter": _filter.model_dump_json()}
        for project in cls._paginate(url=cls._get_url(), params=params):
            yield cls._from_dict(data=project)

    @classmethod
    @handle_api_error
    def create(cls, name: str, project_id: UUID | str) -> Application:
        """Create a new application in a project.

        Creates a new application within the specified project on the Fiddler platform.
        The application must have a unique name within the project.

        Args:
            name: Application name, must be unique within the project.
            project_id: The UUID of the project to create the application in.
                       Can be provided as a UUID object or string representation.

        Returns:
            :class:`~fiddler.entities.Application`: The newly created application instance with server-assigned fields.

        Raises:
            Conflict: If an application with the same name already exists in the project.
            ValidationError: If the application configuration is invalid (e.g., invalid name format).
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get project instance
            project = Project.get_by_name(name="fraud-detection-project")

            # Create a new application for fraud detection
            application = Application.create(
                name="fraud-detection-app",
                project_id=project.id
            )
            print(f"Created application with ID: {application.id}")
            print(f"Created at: {application.created_at}")
            print(f"Project: {application.project.name}")

        Note:
            After successful creation, the application instance is returned with
            server-assigned metadata. The application is immediately available
            for adding datasets, evaluators, and other resources.
        """
        response = cls._client().post(
            url=cls._get_url(),
            json={
                "name": name,
                "project_id": str(project_id),
            },
        )
        application = cls._from_response(response=response)
        logger.info(
            "Application created with id=%s, name=%s", application.id, application.name
        )
        return application

    @classmethod
    @handle_api_error
    def get_or_create(cls, name: str, project_id: UUID | str) -> Application:
        """Get an existing application by name or create a new one if it doesn't exist.

        This is a convenience method that attempts to retrieve an application by name
        within a project, and if not found, creates a new application with that name.
        Useful for idempotent application setup in automation scripts and deployment pipelines.

        Args:
            name: The name of the application to retrieve or create.
            project_id: The UUID of the project to search/create the application in.
                       Can be provided as a UUID object or string representation.

        Returns:
            :class:`~fiddler.entities.Application`: Either the existing application with the specified name,
                  or a newly created application if none existed.

        Raises:
            ValidationError: If the application name format is invalid.
            ApiError: If there's an error communicating with the Fiddler API.

        Example:
            # Get project instance
            project = Project.get_by_name(name="fraud-detection-project")

            # Safe application setup - get existing or create new
            application = Application.get_or_create(
                name="fraud-detection-app",
                project_id=project.id
            )
            print(f"Using application: {application.name} (ID: {application.id})")

            # Idempotent setup in deployment scripts
            application = Application.get_or_create(
                name="llm-pipeline-app",
                project_id=project.id
            )

            # Use in configuration management
            environments = ["dev", "staging", "prod"]
            applications = {}
            for env in environments:
                applications[env] = Application.get_or_create(
                    name=f"fraud-detection-{env}",
                    project_id=project.id
                )

        Note:
            This method is idempotent - calling it multiple times with the same name
            and project_id will return the same application. It logs when creating a new
            application for visibility in automation scenarios.
        """
        try:
            return cls.get_by_name(name=name, project_id=project_id)
        except NotFound:
            logger.info("Application not found, creating a new one - %s", name)
            return Application.create(name=name, project_id=project_id)
