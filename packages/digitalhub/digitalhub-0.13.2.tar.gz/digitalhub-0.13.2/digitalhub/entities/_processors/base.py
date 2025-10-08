# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing

from digitalhub.context.api import delete_context
from digitalhub.entities._commons.enums import ApiCategories, BackendOperations
from digitalhub.factory.factory import factory
from digitalhub.stores.client.api import get_client
from digitalhub.utils.exceptions import EntityAlreadyExistsError, EntityError, EntityNotExistsError
from digitalhub.utils.io_utils import read_yaml

if typing.TYPE_CHECKING:
    from digitalhub.entities.project._base.entity import Project
    from digitalhub.stores.client._base.client import Client


class BaseEntityOperationsProcessor:
    """
    Processor for base entity operations.

    This class handles CRUD operations and other entity management tasks
    for base-level entities (primarily projects). It interacts with the
    client layer to perform backend operations and manages entity lifecycle
    including creation, reading, updating, deletion, and sharing.
    """

    ##############################
    # CRUD base entity
    ##############################

    def _create_base_entity(
        self,
        client: Client,
        entity_type: str,
        entity_dict: dict,
        **kwargs,
    ) -> dict:
        """
        Create a base entity in the backend.

        Builds the appropriate API endpoint and sends a create request
        to the backend for base-level entities.

        Parameters
        ----------
        client : Client
            The client instance to use for the API call.
        entity_type : str
            The type of entity to create (e.g., 'project').
        entity_dict : dict
            The entity data dictionary to create.
        **kwargs : dict
            Additional parameters to pass to the API call.

        Returns
        -------
        dict
            The created entity data returned from the backend.
        """
        api = client.build_api(
            ApiCategories.BASE.value,
            BackendOperations.CREATE.value,
            entity_type=entity_type,
        )
        return client.create_object(api, entity_dict, **kwargs)

    def create_project_entity(
        self,
        _entity: Project | None = None,
        **kwargs,
    ) -> Project:
        """
        Create a project entity in the backend.

        Creates a new project either from an existing entity object or
        by building one from the provided parameters. Handles both
        local and remote backend creation.

        Parameters
        ----------
        _entity : Project, optional
            An existing project entity object to create. If None,
            a new entity will be built from kwargs.
        **kwargs : dict
            Parameters for entity creation, including 'local' flag
            and entity-specific parameters.

        Returns
        -------
        Project
            The created project entity with backend data populated.
        """
        if _entity is not None:
            client = _entity._client
            obj = _entity
        else:
            client = get_client(kwargs.get("local"))
            obj = factory.build_entity_from_params(**kwargs)
        ent = self._create_base_entity(client, obj.ENTITY_TYPE, obj.to_dict())
        ent["local"] = client.is_local()
        return factory.build_entity_from_dict(ent)

    def _read_base_entity(
        self,
        client: Client,
        entity_type: str,
        entity_name: str,
        **kwargs,
    ) -> dict:
        """
        Read a base entity from the backend.

        Builds the appropriate API endpoint and sends a read request
        to retrieve entity data from the backend.

        Parameters
        ----------
        client : Client
            The client instance to use for the API call.
        entity_type : str
            The type of entity to read (e.g., 'project').
        entity_name : str
            The name identifier of the entity to read.
        **kwargs : dict
            Additional parameters to pass to the API call.

        Returns
        -------
        dict
            The entity data retrieved from the backend.
        """
        api = client.build_api(
            ApiCategories.BASE.value,
            BackendOperations.READ.value,
            entity_type=entity_type,
            entity_name=entity_name,
        )
        return client.read_object(api, **kwargs)

    def read_project_entity(
        self,
        entity_type: str,
        entity_name: str,
        **kwargs,
    ) -> Project:
        """
        Read a project entity from the backend.

        Retrieves project data from the backend and constructs a
        Project entity object with the retrieved data.

        Parameters
        ----------
        entity_type : str
            The type of entity to read (typically 'project').
        entity_name : str
            The name identifier of the project to read.
        **kwargs : dict
            Additional parameters including 'local' flag and
            API call parameters.

        Returns
        -------
        Project
            The project entity object populated with backend data.
        """
        client = get_client(kwargs.pop("local", False))
        obj = self._read_base_entity(client, entity_type, entity_name, **kwargs)
        obj["local"] = client.is_local()
        return factory.build_entity_from_dict(obj)

    def import_project_entity(
        self,
        file: str,
        **kwargs,
    ) -> Project:
        """
        Import a project entity from a YAML file and create it in the backend.

        Reads project configuration from a YAML file, creates a new project
        entity in the backend, and imports any related entities defined
        in the file. Raises an error if the project already exists.

        Parameters
        ----------
        file : str
            Path to the YAML file containing project configuration.
        **kwargs : dict
            Additional parameters including 'local' flag.

        Returns
        -------
        Project
            The imported and created project entity.

        Raises
        ------
        EntityError
            If the project already exists in the backend.
        """
        client = get_client(kwargs.pop("local", False))
        obj: dict = read_yaml(file)
        obj["status"] = {}
        obj["local"] = client.is_local()
        ent: Project = factory.build_entity_from_dict(obj)

        try:
            self._create_base_entity(ent._client, ent.ENTITY_TYPE, ent.to_dict())
        except EntityAlreadyExistsError:
            raise EntityError(f"Entity {ent.name} already exists. If you want to update it, use load instead.")

        # Import related entities
        ent._import_entities(obj)
        ent.refresh()
        return ent

    def load_project_entity(
        self,
        file: str,
        **kwargs,
    ) -> Project:
        """
        Load a project entity from a YAML file and update it in the backend.

        Reads project configuration from a YAML file and updates an existing
        project in the backend. If the project doesn't exist, it creates a
        new one. Also loads any related entities defined in the file.

        Parameters
        ----------
        file : str
            Path to the YAML file containing project configuration.
        **kwargs : dict
            Additional parameters including 'local' flag.

        Returns
        -------
        Project
            The loaded and updated project entity.
        """
        client = get_client(kwargs.pop("local", False))
        obj: dict = read_yaml(file)
        obj["local"] = client.is_local()
        ent: Project = factory.build_entity_from_dict(obj)

        try:
            self._update_base_entity(ent._client, ent.ENTITY_TYPE, ent.name, ent.to_dict())
        except EntityNotExistsError:
            self._create_base_entity(ent._client, ent.ENTITY_TYPE, ent.to_dict())

        # Load related entities
        ent._load_entities(obj)
        ent.refresh()
        return ent

    def _list_base_entities(
        self,
        client: Client,
        entity_type: str,
        **kwargs,
    ) -> list[dict]:
        """
        List base entities from the backend.

        Builds the appropriate API endpoint and sends a list request
        to retrieve multiple entities from the backend.

        Parameters
        ----------
        client : Client
            The client instance to use for the API call.
        entity_type : str
            The type of entities to list (e.g., 'project').
        **kwargs : dict
            Additional parameters to pass to the API call for filtering
            or pagination.

        Returns
        -------
        list[dict]
            List of entity data dictionaries from the backend.
        """
        api = client.build_api(
            ApiCategories.BASE.value,
            BackendOperations.LIST.value,
            entity_type=entity_type,
        )
        return client.list_objects(api, **kwargs)

    def list_project_entities(
        self,
        entity_type: str,
        **kwargs,
    ) -> list[Project]:
        """
        List project entities from the backend.

        Retrieves a list of projects from the backend and converts
        them to Project entity objects.

        Parameters
        ----------
        entity_type : str
            The type of entities to list (typically 'project').
        **kwargs : dict
            Additional parameters including 'local' flag and
            API call parameters for filtering or pagination.

        Returns
        -------
        list[Project]
            List of project entity objects.
        """
        client = get_client(kwargs.pop("local", False))
        objs = self._list_base_entities(client, entity_type, **kwargs)
        entities = []
        for obj in objs:
            obj["local"] = client.is_local()
            ent = factory.build_entity_from_dict(obj)
            entities.append(ent)
        return entities

    def _update_base_entity(
        self,
        client: Client,
        entity_type: str,
        entity_name: str,
        entity_dict: dict,
        **kwargs,
    ) -> dict:
        """
        Update a base entity in the backend.

        Builds the appropriate API endpoint and sends an update request
        to modify an existing entity in the backend.

        Parameters
        ----------
        client : Client
            The client instance to use for the API call.
        entity_type : str
            The type of entity to update (e.g., 'project').
        entity_name : str
            The name identifier of the entity to update.
        entity_dict : dict
            The updated entity data dictionary.
        **kwargs : dict
            Additional parameters to pass to the API call.

        Returns
        -------
        dict
            The updated entity data returned from the backend.
        """
        api = client.build_api(
            ApiCategories.BASE.value,
            BackendOperations.UPDATE.value,
            entity_type=entity_type,
            entity_name=entity_name,
        )
        return client.update_object(api, entity_dict, **kwargs)

    def update_project_entity(
        self,
        entity_type: str,
        entity_name: str,
        entity_dict: dict,
        **kwargs,
    ) -> Project:
        """
        Update a project entity in the backend.

        Updates an existing project with new data and returns the
        updated Project entity object.

        Parameters
        ----------
        entity_type : str
            The type of entity to update (typically 'project').
        entity_name : str
            The name identifier of the project to update.
        entity_dict : dict
            The updated project data dictionary.
        **kwargs : dict
            Additional parameters including 'local' flag and
            API call parameters.

        Returns
        -------
        Project
            The updated project entity object.
        """
        client = get_client(kwargs.pop("local", False))
        obj = self._update_base_entity(client, entity_type, entity_name, entity_dict, **kwargs)
        obj["local"] = client.is_local()
        return factory.build_entity_from_dict(obj)

    def _delete_base_entity(
        self,
        client: Client,
        entity_type: str,
        entity_name: str,
        **kwargs,
    ) -> dict:
        """
        Delete a base entity from the backend.

        Builds the appropriate API endpoint and parameters, then sends
        a delete request to remove the entity from the backend.

        Parameters
        ----------
        client : Client
            The client instance to use for the API call.
        entity_type : str
            The type of entity to delete (e.g., 'project').
        entity_name : str
            The name identifier of the entity to delete.
        **kwargs : dict
            Additional parameters to pass to the API call, such as
            cascade deletion options.

        Returns
        -------
        dict
            Response data from the backend delete operation.
        """
        kwargs = client.build_parameters(
            ApiCategories.BASE.value,
            BackendOperations.DELETE.value,
            **kwargs,
        )
        api = client.build_api(
            ApiCategories.BASE.value,
            BackendOperations.DELETE.value,
            entity_type=entity_type,
            entity_name=entity_name,
        )
        return client.delete_object(api, **kwargs)

    def delete_project_entity(
        self,
        entity_type: str,
        entity_name: str,
        **kwargs,
    ) -> dict:
        """
        Delete a project entity from the backend.

        Deletes a project from the backend and optionally cleans up
        the associated context. Handles both local and remote backends.

        Parameters
        ----------
        entity_type : str
            The type of entity to delete (typically 'project').
        entity_name : str
            The name identifier of the project to delete.
        **kwargs : dict
            Additional parameters including 'local' flag, 'clean_context'
            flag (default True), and API call parameters.

        Returns
        -------
        dict
            Response data from the backend delete operation.
        """
        if kwargs.pop("clean_context", True):
            delete_context(entity_name)
        client = get_client(kwargs.pop("local", False))
        return self._delete_base_entity(
            client,
            entity_type,
            entity_name,
            **kwargs,
        )

    ##############################
    # Base entity operations
    ##############################

    def _build_base_entity_key(
        self,
        client: Client,
        entity_id: str,
    ) -> str:
        """
        Build a storage key for a base entity.

        Creates a standardized key string that can be used to identify
        and store the entity in various contexts.

        Parameters
        ----------
        client : Client
            The client instance to use for key building.
        entity_id : str
            The unique identifier of the entity.

        Returns
        -------
        str
            The constructed entity key string.
        """
        return client.build_key(ApiCategories.BASE.value, entity_id)

    def build_project_key(
        self,
        entity_id: str,
        **kwargs,
    ) -> str:
        """
        Build a storage key for a project entity.

        Creates a standardized key string for project identification
        and storage, handling both local and remote client contexts.

        Parameters
        ----------
        entity_id : str
            The unique identifier of the project entity.
        **kwargs : dict
            Additional parameters including 'local' flag.

        Returns
        -------
        str
            The constructed project entity key string.
        """
        client = get_client(kwargs.pop("local", False))
        return self._build_base_entity_key(client, entity_id)

    def share_project_entity(
        self,
        entity_type: str,
        entity_name: str,
        **kwargs,
    ) -> None:
        """
        Share or unshare a project entity with a user.

        Manages project access permissions by sharing the project with
        a specified user or removing user access. Handles both sharing
        and unsharing operations based on the 'unshare' parameter.

        Parameters
        ----------
        entity_type : str
            The type of entity to share (typically 'project').
        entity_name : str
            The name identifier of the project to share.
        **kwargs : dict
            Additional parameters including:
            - 'user': username to share with/unshare from
            - 'unshare': boolean flag for unsharing (default False)
            - 'local': boolean flag for local backend

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If trying to unshare from a user who doesn't have access.
        """
        client = get_client(kwargs.pop("local", False))
        api = client.build_api(
            ApiCategories.BASE.value,
            BackendOperations.SHARE.value,
            entity_type=entity_type,
            entity_name=entity_name,
        )

        user = kwargs.pop("user", None)
        if unshare := kwargs.pop("unshare", False):
            users = client.read_object(api, **kwargs)
            for u in users:
                if u["user"] == user:
                    kwargs["id"] = u["id"]
                break
            else:
                raise ValueError(f"User '{user}' does not have access to project.")

        kwargs = client.build_parameters(
            ApiCategories.BASE.value,
            BackendOperations.SHARE.value,
            unshare=unshare,
            user=user,
            **kwargs,
        )
        if unshare:
            client.delete_object(api, **kwargs)
            return
        client.create_object(api, obj={}, **kwargs)


base_processor = BaseEntityOperationsProcessor()
