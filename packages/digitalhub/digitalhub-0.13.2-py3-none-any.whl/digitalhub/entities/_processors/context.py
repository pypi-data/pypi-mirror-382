# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing
from typing import Any

from digitalhub.entities._commons.enums import ApiCategories, BackendOperations, Relationship, State
from digitalhub.entities._processors.utils import (
    get_context_from_identifier,
    get_context_from_project,
    parse_identifier,
)
from digitalhub.factory.factory import factory
from digitalhub.utils.exceptions import EntityAlreadyExistsError, EntityError, EntityNotExistsError
from digitalhub.utils.io_utils import read_yaml
from digitalhub.utils.types import SourcesOrListOfSources

if typing.TYPE_CHECKING:
    from digitalhub.context.context import Context
    from digitalhub.entities._base.context.entity import ContextEntity
    from digitalhub.entities._base.executable.entity import ExecutableEntity
    from digitalhub.entities._base.material.entity import MaterialEntity
    from digitalhub.entities._base.unversioned.entity import UnversionedEntity


class ContextEntityOperationsProcessor:
    """
    Processor for context entity operations.

    This class handles CRUD operations and other entity management tasks
    for context-level entities (artifacts, functions, workflows, runs, etc.)
    within projects. It manages the full lifecycle of versioned and
    unversioned entities including creation, reading, updating, deletion,
    import/export, and specialized operations like file uploads and metrics.
    """

    ##############################
    # CRUD context entity
    ##############################

    def _create_context_entity(
        self,
        context: Context,
        entity_type: str,
        entity_dict: dict,
    ) -> dict:
        """
        Create a context entity in the backend.

        Builds the appropriate API endpoint and sends a create request
        to the backend for context-level entities within a project.

        Parameters
        ----------
        context : Context
            The project context instance.
        entity_type : str
            The type of entity to create (e.g., 'artifact', 'function').
        entity_dict : dict
            The entity data dictionary to create.

        Returns
        -------
        dict
            The created entity data returned from the backend.
        """
        api = context.client.build_api(
            ApiCategories.CONTEXT.value,
            BackendOperations.CREATE.value,
            project=context.name,
            entity_type=entity_type,
        )
        return context.client.create_object(api, entity_dict)

    def create_context_entity(
        self,
        _entity: ContextEntity | None = None,
        **kwargs,
    ) -> ContextEntity:
        """
        Create a context entity in the backend.

        Creates a new context entity either from an existing entity object
        or by building one from the provided parameters. Handles entity
        creation within a project context.

        Parameters
        ----------
        _entity : ContextEntity, optional
            An existing context entity object to create. If None,
            a new entity will be built from kwargs.
        **kwargs : dict
            Parameters for entity creation, including 'project' and
            entity-specific parameters.

        Returns
        -------
        ContextEntity
            The created context entity with backend data populated.
        """
        if _entity is not None:
            context = _entity._context()
            obj = _entity
        else:
            context = get_context_from_project(kwargs["project"])
            obj: ContextEntity = factory.build_entity_from_params(**kwargs)
        new_obj = self._create_context_entity(context, obj.ENTITY_TYPE, obj.to_dict())
        return factory.build_entity_from_dict(new_obj)

    def log_material_entity(
        self,
        **kwargs,
    ) -> MaterialEntity:
        """
        Create a material entity in the backend and upload associated files.

        Creates a new material entity (artifact, dataitem, or model) and
        handles file upload operations. Manages upload state transitions
        and error handling during the upload process.

        Parameters
        ----------
        **kwargs : dict
            Parameters for entity creation including:
            - 'source': file source(s) to upload
            - 'project': project name
            - other entity-specific parameters

        Returns
        -------
        MaterialEntity
            The created material entity with uploaded files.

        Raises
        ------
        EntityError
            If file upload fails during the process.
        """
        source: SourcesOrListOfSources = kwargs.pop("source")
        context = get_context_from_project(kwargs["project"])
        obj = factory.build_entity_from_params(**kwargs)
        if context.is_running:
            obj.add_relationship(Relationship.PRODUCEDBY.value, context.get_run_ctx())

        new_obj: MaterialEntity = self._create_context_entity(context, obj.ENTITY_TYPE, obj.to_dict())
        new_obj = factory.build_entity_from_dict(new_obj)

        new_obj.status.state = State.UPLOADING.value
        new_obj = self._update_material_entity(new_obj)

        # Handle file upload
        try:
            new_obj.upload(source)
            uploaded = True
            msg = None
        except Exception as e:
            uploaded = False
            msg = str(e.args)

        new_obj.status.message = msg

        # Update status after upload
        if uploaded:
            new_obj.status.state = State.READY.value
            new_obj = self._update_material_entity(new_obj)
        else:
            new_obj.status.state = State.ERROR.value
            new_obj = self._update_material_entity(new_obj)
            raise EntityError(msg)

        return new_obj

    def _read_context_entity(
        self,
        context: Context,
        identifier: str,
        entity_type: str | None = None,
        project: str | None = None,
        entity_id: str | None = None,
        **kwargs,
    ) -> dict:
        """
        Read a context entity from the backend.

        Retrieves entity data from the backend using either entity ID
        for direct access or entity name for latest version lookup.
        Handles both specific version reads and latest version queries.

        Parameters
        ----------
        context : Context
            The project context instance.
        identifier : str
            Entity key (store://...) or entity name identifier.
        entity_type : str, optional
            The type of entity to read.
        project : str, optional
            Project name (used for identifier parsing).
        entity_id : str, optional
            Specific entity ID to read.
        **kwargs : dict
            Additional parameters to pass to the API call.

        Returns
        -------
        dict
            The entity data retrieved from the backend.
        """
        project, entity_type, _, entity_name, entity_id = parse_identifier(
            identifier,
            project=project,
            entity_type=entity_type,
            entity_id=entity_id,
        )

        if entity_id is None:
            kwargs["entity_name"] = entity_name
        kwargs = context.client.build_parameters(
            ApiCategories.CONTEXT.value,
            BackendOperations.READ.value,
            **kwargs,
        )

        if entity_id is None:
            api = context.client.build_api(
                ApiCategories.CONTEXT.value,
                BackendOperations.LIST.value,
                project=context.name,
                entity_type=entity_type,
            )
            return context.client.list_first_object(api, **kwargs)

        api = context.client.build_api(
            ApiCategories.CONTEXT.value,
            BackendOperations.READ.value,
            project=context.name,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        return context.client.read_object(api, **kwargs)

    def read_context_entity(
        self,
        identifier: str,
        entity_type: str | None = None,
        project: str | None = None,
        entity_id: str | None = None,
        **kwargs,
    ) -> ContextEntity:
        """
        Read a context entity from the backend.

        Retrieves entity data from the backend and constructs a context
        entity object. Handles post-processing for metrics and file info.

        Parameters
        ----------
        identifier : str
            Entity key (store://...) or entity name identifier.
        entity_type : str, optional
            The type of entity to read.
        project : str, optional
            Project name for context resolution.
        entity_id : str, optional
            Specific entity ID to read.
        **kwargs : dict
            Additional parameters to pass to the API call.

        Returns
        -------
        ContextEntity
            The context entity object populated with backend data.
        """
        context = get_context_from_identifier(identifier, project)
        obj = self._read_context_entity(
            context,
            identifier,
            entity_type=entity_type,
            project=project,
            entity_id=entity_id,
            **kwargs,
        )
        entity = factory.build_entity_from_dict(obj)
        return self._post_process_get(entity)

    def read_unversioned_entity(
        self,
        identifier: str,
        entity_type: str | None = None,
        project: str | None = None,
        entity_id: str | None = None,
        **kwargs,
    ) -> UnversionedEntity:
        """
        Read an unversioned entity from the backend.

        Retrieves unversioned entity data (runs, tasks) from the backend.
        Handles identifier parsing for entities that don't follow the
        standard versioned naming convention.

        Parameters
        ----------
        identifier : str
            Entity key (store://...) or entity ID.
        entity_type : str, optional
            The type of entity to read.
        project : str, optional
            Project name for context resolution.
        entity_id : str, optional
            Specific entity ID to read.
        **kwargs : dict
            Additional parameters to pass to the API call.

        Returns
        -------
        UnversionedEntity
            The unversioned entity object populated with backend data.
        """
        if not identifier.startswith("store://"):
            entity_id = identifier
        else:
            splt = identifier.split(":")
            if len(splt) == 3:
                identifier = f"{splt[0]}:{splt[1]}"
        return self.read_context_entity(
            identifier,
            entity_type=entity_type,
            project=project,
            entity_id=entity_id,
            **kwargs,
        )

    def import_context_entity(
        self,
        file: str,
    ) -> ContextEntity:
        """
        Import a context entity from a YAML file and create it in the backend.

        Reads entity configuration from a YAML file and creates a new
        context entity in the backend. Raises an error if the entity
        already exists.

        Parameters
        ----------
        file : str
            Path to the YAML file containing entity configuration.

        Returns
        -------
        ContextEntity
            The imported and created context entity.

        Raises
        ------
        EntityError
            If the entity already exists in the backend.
        """
        dict_obj: dict = read_yaml(file)
        dict_obj["status"] = {}
        context = get_context_from_project(dict_obj["project"])
        obj = factory.build_entity_from_dict(dict_obj)
        try:
            self._create_context_entity(context, obj.ENTITY_TYPE, obj.to_dict())
        except EntityAlreadyExistsError:
            raise EntityError(f"Entity {obj.name} already exists. If you want to update it, use load instead.")
        return obj

    def import_executable_entity(
        self,
        file: str,
    ) -> ExecutableEntity:
        """
        Import an executable entity from a YAML file and create it in the backend.

        Reads executable entity configuration from a YAML file and creates
        a new executable entity (function or workflow) in the backend.
        Also imports associated task definitions if present in the file.

        Parameters
        ----------
        file : str
            Path to the YAML file containing executable entity configuration.
            Can contain a single entity or a list with the executable and tasks.

        Returns
        -------
        ExecutableEntity
            The imported and created executable entity.

        Raises
        ------
        EntityError
            If the entity already exists in the backend.
        """
        dict_obj: dict | list[dict] = read_yaml(file)
        if isinstance(dict_obj, list):
            exec_dict = dict_obj[0]
            exec_dict["status"] = {}
            tsk_dicts = []
            for i in dict_obj[1:]:
                i["status"] = {}
                tsk_dicts.append(i)
        else:
            exec_dict = dict_obj
            tsk_dicts = []

        context = get_context_from_project(exec_dict["project"])
        obj: ExecutableEntity = factory.build_entity_from_dict(exec_dict)
        try:
            self._create_context_entity(context, obj.ENTITY_TYPE, obj.to_dict())
        except EntityAlreadyExistsError:
            raise EntityError(f"Entity {obj.name} already exists. If you want to update it, use load instead.")

        obj.import_tasks(tsk_dicts)

        return obj

    def load_context_entity(
        self,
        file: str,
    ) -> ContextEntity:
        """
        Load a context entity from a YAML file and update it in the backend.

        Reads entity configuration from a YAML file and updates an existing
        entity in the backend. If the entity doesn't exist, it creates a
        new one.

        Parameters
        ----------
        file : str
            Path to the YAML file containing entity configuration.

        Returns
        -------
        ContextEntity
            The loaded and updated context entity.
        """
        dict_obj: dict = read_yaml(file)
        context = get_context_from_project(dict_obj["project"])
        obj: ContextEntity = factory.build_entity_from_dict(dict_obj)
        try:
            self._update_context_entity(context, obj.ENTITY_TYPE, obj.id, obj.to_dict())
        except EntityNotExistsError:
            self._create_context_entity(context, obj.ENTITY_TYPE, obj.to_dict())
        return obj

    def load_executable_entity(
        self,
        file: str,
    ) -> ExecutableEntity:
        """
        Load an executable entity from a YAML file and update it in the backend.

        Reads executable entity configuration from a YAML file and updates
        an existing executable entity in the backend. If the entity doesn't
        exist, it creates a new one. Also handles task imports.

        Parameters
        ----------
        file : str
            Path to the YAML file containing executable entity configuration.
            Can contain a single entity or a list with the executable and tasks.

        Returns
        -------
        ExecutableEntity
            The loaded and updated executable entity.
        """
        dict_obj: dict | list[dict] = read_yaml(file)
        if isinstance(dict_obj, list):
            exec_dict = dict_obj[0]
            tsk_dicts = dict_obj[1:]
        else:
            exec_dict = dict_obj
            tsk_dicts = []

        context = get_context_from_project(exec_dict["project"])
        obj: ExecutableEntity = factory.build_entity_from_dict(exec_dict)

        try:
            self._update_context_entity(context, obj.ENTITY_TYPE, obj.id, obj.to_dict())
        except EntityNotExistsError:
            self._create_context_entity(context, obj.ENTITY_TYPE, obj.to_dict())
        obj.import_tasks(tsk_dicts)
        return obj

    def _read_context_entity_versions(
        self,
        context: Context,
        identifier: str,
        entity_type: str | None = None,
        project: str | None = None,
        **kwargs,
    ) -> list[dict]:
        """
        Read all versions of a context entity from the backend.

        Retrieves all available versions of a named entity from the
        backend using the entity name identifier.

        Parameters
        ----------
        context : Context
            The project context instance.
        identifier : str
            Entity key (store://...) or entity name identifier.
        entity_type : str, optional
            The type of entity to read versions for.
        project : str, optional
            Project name (used for identifier parsing).
        **kwargs : dict
            Additional parameters to pass to the API call.

        Returns
        -------
        list[dict]
            List of entity data dictionaries for all versions.
        """
        project, entity_type, _, entity_name, _ = parse_identifier(
            identifier,
            project=project,
            entity_type=entity_type,
        )

        kwargs = context.client.build_parameters(
            ApiCategories.CONTEXT.value,
            BackendOperations.READ_ALL_VERSIONS.value,
            entity_name=entity_name,
            **kwargs,
        )

        api = context.client.build_api(
            ApiCategories.CONTEXT.value,
            BackendOperations.LIST.value,
            project=context.name,
            entity_type=entity_type,
        )
        return context.client.list_objects(api, **kwargs)

    def read_context_entity_versions(
        self,
        identifier: str,
        entity_type: str | None = None,
        project: str | None = None,
        **kwargs,
    ) -> list[ContextEntity]:
        """
        Read all versions of a context entity from the backend.

        Retrieves all available versions of a named entity and constructs
        context entity objects for each version. Applies post-processing
        for metrics and file info.

        Parameters
        ----------
        identifier : str
            Entity key (store://...) or entity name identifier.
        entity_type : str, optional
            The type of entity to read versions for.
        project : str, optional
            Project name for context resolution.
        **kwargs : dict
            Additional parameters to pass to the API call.

        Returns
        -------
        list[ContextEntity]
            List of context entity objects for all versions.
        """
        context = get_context_from_identifier(identifier, project)
        objs = self._read_context_entity_versions(
            context,
            identifier,
            entity_type=entity_type,
            project=project,
            **kwargs,
        )
        objects = []
        for o in objs:
            entity: ContextEntity = factory.build_entity_from_dict(o)
            entity = self._post_process_get(entity)
            objects.append(entity)
        return objects

    def _list_context_entities(
        self,
        context: Context,
        entity_type: str,
        **kwargs,
    ) -> list[dict]:
        """
        List context entities from the backend.

        Retrieves a list of entities of a specific type from the backend
        within the project context.

        Parameters
        ----------
        context : Context
            The project context instance.
        entity_type : str
            The type of entities to list.
        **kwargs : dict
            Additional parameters to pass to the API call for filtering
            or pagination.

        Returns
        -------
        list[dict]
            List of entity data dictionaries from the backend.
        """
        api = context.client.build_api(
            ApiCategories.CONTEXT.value,
            BackendOperations.LIST.value,
            project=context.name,
            entity_type=entity_type,
        )
        return context.client.list_objects(api, **kwargs)

    def list_context_entities(
        self,
        project: str,
        entity_type: str,
        **kwargs,
    ) -> list[ContextEntity]:
        """
        List all latest version context entities from the backend.

        Retrieves a list of entities of a specific type from the backend
        and constructs context entity objects. Only returns the latest
        version of each entity. Applies post-processing for metrics and
        file info.

        Parameters
        ----------
        project : str
            The project name to list entities from.
        entity_type : str
            The type of entities to list.
        **kwargs : dict
            Additional parameters to pass to the API call for filtering
            or pagination.

        Returns
        -------
        list[ContextEntity]
            List of context entity objects (latest versions only).
        """
        context = get_context_from_project(project)
        objs = self._list_context_entities(context, entity_type, **kwargs)
        objects = []
        for o in objs:
            entity: ContextEntity = factory.build_entity_from_dict(o)
            entity = self._post_process_get(entity)
            objects.append(entity)
        return objects

    def _update_material_entity(
        self,
        new_obj: MaterialEntity,
    ) -> dict:
        """
        Update a material entity using a shortcut method.

        Convenience method for updating material entities during
        file upload operations.

        Parameters
        ----------
        new_obj : MaterialEntity
            The material entity object to update.

        Returns
        -------
        dict
            Response data from the backend update operation.
        """
        return self.update_context_entity(
            new_obj.project,
            new_obj.ENTITY_TYPE,
            new_obj.id,
            new_obj.to_dict(),
        )

    def _update_context_entity(
        self,
        context: Context,
        entity_type: str,
        entity_id: str,
        entity_dict: dict,
        **kwargs,
    ) -> dict:
        """
        Update a context entity in the backend.

        Updates an existing context entity with new data. Entity
        specifications are typically immutable, so this primarily
        updates status and metadata.

        Parameters
        ----------
        context : Context
            The project context instance.
        entity_type : str
            The type of entity to update.
        entity_id : str
            The unique identifier of the entity to update.
        entity_dict : dict
            The updated entity data dictionary.
        **kwargs : dict
            Additional parameters to pass to the API call.

        Returns
        -------
        dict
            Response data from the backend update operation.
        """
        api = context.client.build_api(
            ApiCategories.CONTEXT.value,
            BackendOperations.UPDATE.value,
            project=context.name,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        return context.client.update_object(api, entity_dict, **kwargs)

    def update_context_entity(
        self,
        project: str,
        entity_type: str,
        entity_id: str,
        entity_dict: dict,
        **kwargs,
    ) -> ContextEntity:
        """
        Update a context entity in the backend.

        Updates an existing context entity with new data and returns
        the updated context entity object. Entity specifications are
        typically immutable.

        Parameters
        ----------
        project : str
            The project name containing the entity.
        entity_type : str
            The type of entity to update.
        entity_id : str
            The unique identifier of the entity to update.
        entity_dict : dict
            The updated entity data dictionary.
        **kwargs : dict
            Additional parameters to pass to the API call.

        Returns
        -------
        ContextEntity
            The updated context entity object.
        """
        context = get_context_from_project(project)
        obj = self._update_context_entity(
            context,
            entity_type,
            entity_id,
            entity_dict,
            **kwargs,
        )
        return factory.build_entity_from_dict(obj)

    def _delete_context_entity(
        self,
        context: Context,
        identifier: str,
        entity_type: str | None = None,
        project: str | None = None,
        entity_id: str | None = None,
        **kwargs,
    ) -> dict:
        """
        Delete a context entity from the backend.

        Removes an entity from the backend, with options for deleting
        specific versions or all versions of a named entity. Handles
        cascade deletion if supported.

        Parameters
        ----------
        context : Context
            The project context instance.
        identifier : str
            Entity key (store://...) or entity name identifier.
        entity_type : str, optional
            The type of entity to delete.
        project : str, optional
            Project name (used for identifier parsing).
        entity_id : str, optional
            Specific entity ID to delete.
        **kwargs : dict
            Additional parameters including:
            - 'delete_all_versions': delete all versions of named entity
            - 'cascade': cascade deletion options

        Returns
        -------
        dict
            Response data from the backend delete operation.
        """
        project, entity_type, _, entity_name, entity_id = parse_identifier(
            identifier,
            project=project,
            entity_type=entity_type,
            entity_id=entity_id,
        )

        delete_all_versions: bool = kwargs.pop("delete_all_versions", False)
        kwargs = context.client.build_parameters(
            ApiCategories.CONTEXT.value,
            BackendOperations.DELETE.value,
            entity_id=entity_id,
            entity_name=entity_name,
            cascade=kwargs.pop("cascade", None),
            delete_all_versions=delete_all_versions,
            **kwargs,
        )

        if delete_all_versions:
            api = context.client.build_api(
                ApiCategories.CONTEXT.value,
                BackendOperations.LIST.value,
                project=context.name,
                entity_type=entity_type,
            )
        else:
            api = context.client.build_api(
                ApiCategories.CONTEXT.value,
                BackendOperations.DELETE.value,
                project=context.name,
                entity_type=entity_type,
                entity_id=entity_id,
            )
        return context.client.delete_object(api, **kwargs)

    def delete_context_entity(
        self,
        identifier: str,
        project: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        **kwargs,
    ) -> dict:
        """
        Delete a context entity from the backend.

        Removes an entity from the backend with support for deleting
        specific versions or all versions of a named entity.

        Parameters
        ----------
        identifier : str
            Entity key (store://...) or entity name identifier.
        project : str, optional
            Project name for context resolution.
        entity_type : str, optional
            The type of entity to delete.
        entity_id : str, optional
            Specific entity ID to delete.
        **kwargs : dict
            Additional parameters including deletion options.

        Returns
        -------
        dict
            Response data from the backend delete operation.
        """
        context = get_context_from_identifier(identifier, project)
        return self._delete_context_entity(
            context,
            identifier,
            entity_type,
            context.name,
            entity_id,
            **kwargs,
        )

    def _post_process_get(self, entity: ContextEntity) -> ContextEntity:
        """
        Post-process a retrieved context entity.

        Applies additional processing to entities after retrieval,
        including loading metrics and file information if available.

        Parameters
        ----------
        entity : ContextEntity
            The entity to post-process.

        Returns
        -------
        ContextEntity
            The post-processed entity with additional data loaded.
        """
        if hasattr(entity.status, "metrics"):
            entity._get_metrics()
        if hasattr(entity.status, "files"):
            entity._get_files_info()
        return entity

    ##############################
    # Context entity operations
    ##############################

    def _build_context_entity_key(
        self,
        context: Context,
        entity_type: str,
        entity_kind: str,
        entity_name: str,
        entity_id: str | None = None,
    ) -> str:
        """
        Build a storage key for a context entity.

        Creates a standardized key string for context entity identification
        and storage within a project context.

        Parameters
        ----------
        context : Context
            The project context instance.
        entity_type : str
            The type of entity.
        entity_kind : str
            The kind/subtype of entity.
        entity_name : str
            The name of the entity.
        entity_id : str, optional
            The unique identifier of the entity version.

        Returns
        -------
        str
            The constructed context entity key string.
        """
        return context.client.build_key(
            ApiCategories.CONTEXT.value,
            project=context.name,
            entity_type=entity_type,
            entity_kind=entity_kind,
            entity_name=entity_name,
            entity_id=entity_id,
        )

    def build_context_entity_key(
        self,
        project: str,
        entity_type: str,
        entity_kind: str,
        entity_name: str,
        entity_id: str | None = None,
    ) -> str:
        """
        Build a storage key for a context entity.

        Creates a standardized key string for context entity identification
        and storage, resolving the project context automatically.

        Parameters
        ----------
        project : str
            The project name containing the entity.
        entity_type : str
            The type of entity.
        entity_kind : str
            The kind/subtype of entity.
        entity_name : str
            The name of the entity.
        entity_id : str, optional
            The unique identifier of the entity version.

        Returns
        -------
        str
            The constructed context entity key string.
        """
        context = get_context_from_project(project)
        return self._build_context_entity_key(context, entity_type, entity_kind, entity_name, entity_id)

    def read_secret_data(
        self,
        project: str,
        entity_type: str,
        **kwargs,
    ) -> dict:
        """
        Read secret data from the backend.

        Retrieves secret data stored in the backend for a specific
        project and entity type.

        Parameters
        ----------
        project : str
            The project name containing the secrets.
        entity_type : str
            The type of entity (typically 'secret').
        **kwargs : dict
            Additional parameters to pass to the API call.

        Returns
        -------
        dict
            Secret data retrieved from the backend.
        """
        context = get_context_from_project(project)
        api = context.client.build_api(
            ApiCategories.CONTEXT.value,
            BackendOperations.DATA.value,
            project=context.name,
            entity_type=entity_type,
        )
        return context.client.read_object(api, **kwargs)

    def update_secret_data(
        self,
        project: str,
        entity_type: str,
        data: dict,
        **kwargs,
    ) -> None:
        """
        Update secret data in the backend.

        Stores or updates secret data in the backend for a specific
        project and entity type.

        Parameters
        ----------
        project : str
            The project name to store secrets in.
        entity_type : str
            The type of entity (typically 'secret').
        data : dict
            The secret data dictionary to store.
        **kwargs : dict
            Additional parameters to pass to the API call.

        Returns
        -------
        None
        """
        context = get_context_from_project(project)
        api = context.client.build_api(
            ApiCategories.CONTEXT.value,
            BackendOperations.DATA.value,
            project=context.name,
            entity_type=entity_type,
        )
        context.client.update_object(api, data, **kwargs)

    def read_run_logs(
        self,
        project: str,
        entity_type: str,
        entity_id: str,
        **kwargs,
    ) -> dict:
        """
        Read execution logs from the backend.

        Retrieves logs for a specific run or task execution from
        the backend.

        Parameters
        ----------
        project : str
            The project name containing the entity.
        entity_type : str
            The type of entity (typically 'run' or 'task').
        entity_id : str
            The unique identifier of the entity to get logs for.
        **kwargs : dict
            Additional parameters to pass to the API call.

        Returns
        -------
        dict
            Log data retrieved from the backend.
        """
        context = get_context_from_project(project)
        api = context.client.build_api(
            ApiCategories.CONTEXT.value,
            BackendOperations.LOGS.value,
            project=context.name,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        return context.client.read_object(api, **kwargs)

    def stop_entity(
        self,
        project: str,
        entity_type: str,
        entity_id: str,
        **kwargs,
    ) -> None:
        """
        Stop a running entity in the backend.

        Sends a stop signal to halt execution of a running entity
        such as a workflow or long-running task.

        Parameters
        ----------
        project : str
            The project name containing the entity.
        entity_type : str
            The type of entity to stop.
        entity_id : str
            The unique identifier of the entity to stop.
        **kwargs : dict
            Additional parameters to pass to the API call.

        Returns
        -------
        None
        """
        context = get_context_from_project(project)
        api = context.client.build_api(
            ApiCategories.CONTEXT.value,
            BackendOperations.STOP.value,
            project=context.name,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        context.client.create_object(api, **kwargs)

    def resume_entity(
        self,
        project: str,
        entity_type: str,
        entity_id: str,
        **kwargs,
    ) -> None:
        """
        Resume a stopped entity in the backend.

        Sends a resume signal to restart execution of a previously
        stopped entity such as a workflow or task.

        Parameters
        ----------
        project : str
            The project name containing the entity.
        entity_type : str
            The type of entity to resume.
        entity_id : str
            The unique identifier of the entity to resume.
        **kwargs : dict
            Additional parameters to pass to the API call.

        Returns
        -------
        None
        """
        context = get_context_from_project(project)
        api = context.client.build_api(
            ApiCategories.CONTEXT.value,
            BackendOperations.RESUME.value,
            project=context.name,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        context.client.create_object(api, **kwargs)

    def read_files_info(
        self,
        project: str,
        entity_type: str,
        entity_id: str,
        **kwargs,
    ) -> list[dict]:
        """
        Read file information from the backend.

        Retrieves metadata about files associated with an entity,
        including file paths, sizes, and other attributes.

        Parameters
        ----------
        project : str
            The project name containing the entity.
        entity_type : str
            The type of entity to get file info for.
        entity_id : str
            The unique identifier of the entity.
        **kwargs : dict
            Additional parameters to pass to the API call.

        Returns
        -------
        list[dict]
            List of file information dictionaries from the backend.
        """
        context = get_context_from_project(project)
        api = context.client.build_api(
            ApiCategories.CONTEXT.value,
            BackendOperations.FILES.value,
            project=context.name,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        return context.client.read_object(api, **kwargs)

    def update_files_info(
        self,
        project: str,
        entity_type: str,
        entity_id: str,
        entity_list: list[dict],
        **kwargs,
    ) -> None:
        """
        Get files info from backend.

        Parameters
        ----------
        project : str
            Project name.
        entity_type : str
            Entity type.
        entity_id : str
            Entity ID.
        entity_list : list[dict]
            Entity list.
        **kwargs : dict
            Parameters to pass to the API call.

        Returns
        -------
        None
        """
        context = get_context_from_project(project)
        api = context.client.build_api(
            ApiCategories.CONTEXT.value,
            BackendOperations.FILES.value,
            project=context.name,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        return context.client.update_object(api, entity_list, **kwargs)

    def read_metrics(
        self,
        project: str,
        entity_type: str,
        entity_id: str,
        metric_name: str | None = None,
        **kwargs,
    ) -> dict:
        """
        Read metrics from the backend for a specific entity.

        Retrieves metrics data associated with an entity. Can fetch either
        all metrics or a specific metric by name. Used for performance
        monitoring and analysis of entity operations.

        Parameters
        ----------
        project : str
            The project name containing the entity.
        entity_type : str
            The type of entity to read metrics from.
        entity_id : str
            The unique identifier of the entity.
        metric_name : str, optional
            The name of a specific metric to retrieve.
            If None, retrieves all available metrics.
        **kwargs : dict
            Additional parameters to pass to the API call.

        Returns
        -------
        dict
            Dictionary containing metric data from the backend.
        """
        context = get_context_from_project(project)
        api = context.client.build_api(
            ApiCategories.CONTEXT.value,
            BackendOperations.METRICS.value,
            project=context.name,
            entity_type=entity_type,
            entity_id=entity_id,
            metric_name=metric_name,
        )
        return context.client.read_object(api, **kwargs)

    def update_metric(
        self,
        project: str,
        entity_type: str,
        entity_id: str,
        metric_name: str,
        metric_value: Any,
        **kwargs,
    ) -> None:
        """
        Update or create a metric value for an entity in the backend.

        Updates an existing metric or creates a new one with the specified
        value. Metrics are used for tracking performance, status, and
        other quantitative aspects of entity operations.

        Parameters
        ----------
        project : str
            The project name containing the entity.
        entity_type : str
            The type of entity to update metrics for.
        entity_id : str
            The unique identifier of the entity.
        metric_name : str
            The name of the metric to update or create.
        metric_value : Any
            The value to set for the metric.
            Can be numeric, string, or other supported types.
        **kwargs : dict
            Additional parameters to pass to the API call.

        Returns
        -------
        None
        """
        context = get_context_from_project(project)
        api = context.client.build_api(
            ApiCategories.CONTEXT.value,
            BackendOperations.METRICS.value,
            project=context.name,
            entity_type=entity_type,
            entity_id=entity_id,
            metric_name=metric_name,
        )
        context.client.update_object(api, metric_value, **kwargs)

    def _search(
        self,
        context: Context,
        **kwargs,
    ) -> dict:
        """
        Execute search query against the backend API.

        Internal method that performs the actual search operation
        by building API parameters, executing the search request,
        and processing the results into entity objects.

        Parameters
        ----------
        context : Context
            The context instance containing client and project information.
        **kwargs : dict
            Search parameters and filters to pass to the API call.

        Returns
        -------
        dict
            List of context entity objects matching the search criteria.
        """
        kwargs = context.client.build_parameters(
            ApiCategories.CONTEXT.value,
            BackendOperations.SEARCH.value,
            **kwargs,
        )
        api = context.client.build_api(
            ApiCategories.CONTEXT.value,
            BackendOperations.SEARCH.value,
            project=context.name,
        )
        entities_dict = context.client.read_object(api, **kwargs)
        return [self.read_context_entity(entity["key"]) for entity in entities_dict["content"]]

    def search_entity(
        self,
        project: str,
        query: str | None = None,
        entity_types: list[str] | None = None,
        name: str | None = None,
        kind: str | None = None,
        created: str | None = None,
        updated: str | None = None,
        description: str | None = None,
        labels: list[str] | None = None,
        **kwargs,
    ) -> list[ContextEntity]:
        """
        Search for entities in the backend using various criteria.

        Performs a flexible search across multiple entity attributes,
        allowing for complex queries and filtering. Returns matching
        entities from the project context.

        Parameters
        ----------
        project : str
            The project name to search within.
        query : str, optional
            Free-text search query to match against entity content.
        entity_types : list[str], optional
            List of entity types to filter by.
            If None, searches all entity types.
        name : str, optional
            Entity name pattern to match.
        kind : str, optional
            Entity kind to filter by.
        created : str, optional
            Creation date filter (ISO format).
        updated : str, optional
            Last update date filter (ISO format).
        description : str, optional
            Description pattern to match.
        labels : list[str], optional
            List of label patterns to match.
        **kwargs : dict
            Additional search parameters to pass to the API call.

        Returns
        -------
        list[ContextEntity]
            List of matching entity instances from the search.
        """
        context = get_context_from_project(project)
        return self._search(
            context,
            query=query,
            entity_types=entity_types,
            name=name,
            kind=kind,
            created=created,
            updated=updated,
            description=description,
            labels=labels,
            **kwargs,
        )


context_processor = ContextEntityOperationsProcessor()
