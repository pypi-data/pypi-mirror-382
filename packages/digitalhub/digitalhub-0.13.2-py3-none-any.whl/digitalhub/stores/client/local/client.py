# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from digitalhub.stores.client._base.client import Client
from digitalhub.stores.client.local.api_builder import ClientLocalApiBuilder
from digitalhub.stores.client.local.enums import LocalClientVar
from digitalhub.stores.client.local.key_builder import ClientLocalKeyBuilder
from digitalhub.stores.client.local.params_builder import ClientLocalParametersBuilder
from digitalhub.utils.exceptions import BackendError


class ClientLocal(Client):
    """
    Local client.

    The Local client can be used when a remote Digitalhub backend is not available.
    It handles the creation, reading, updating and deleting of objects in memory,
    storing them in a local dictionary.
    The functionality of the Local client is almost the same as the DHCore client.
    Main differences are:
        - Local client does delete objects on cascade.
        - The run execution are forced to be local.
    """

    def __init__(self) -> None:
        super().__init__()
        self._api_builder = ClientLocalApiBuilder()
        self._key_builder = ClientLocalKeyBuilder()
        self._params_builder = ClientLocalParametersBuilder()
        self._db: dict[str, dict[str, dict]] = {}

    ##############################
    # CRUD
    ##############################

    def create_object(self, api: str, obj: Any, **kwargs) -> dict:
        """
        Create an object in local.

        Parameters
        ----------
        api : str
            Create API.
        obj : dict
            Object to create.

        Returns
        -------
        dict
            The created object.
        """
        if api == LocalClientVar.EMPTY.value:
            return {}
        if not isinstance(obj, dict):
            raise TypeError("Object must be a dictionary")

        entity_type, _, context_api = self._parse_api(api)
        try:
            # Check if entity_type is valid
            if entity_type is None:
                raise TypeError

            # Check if entity_type exists, if not, create a mapping
            self._db.setdefault(entity_type, {})

            # Base API
            #
            # POST /api/v1/projects
            #
            # Project are not versioned, everything is stored on "entity_id" key
            if not context_api:
                if entity_type == "projects":
                    entity_id = obj["name"]
                    if entity_id in self._db[entity_type]:
                        raise ValueError
                    self._db[entity_type][entity_id] = obj

            # Context API
            #
            # POST /api/v1/-/<project-name>/artifacts
            # POST /api/v1/-/<project-name>/functions
            # POST /api/v1/-/<project-name>/runs
            #
            # Runs and tasks are not versioned, so we keep name as entity_id.
            # We have both "name" and "id" attributes for versioned objects so we use them as storage keys.
            # The "latest" key is used to store the latest version of the object.
            else:
                entity_id = obj["id"]
                name = obj.get("name", entity_id)
                self._db[entity_type].setdefault(name, {})
                if entity_id in self._db[entity_type][name]:
                    raise ValueError
                self._db[entity_type][name][entity_id] = obj
                self._db[entity_type][name]["latest"] = obj

            # Return the created object
            return obj

        # Key error are possibly raised by accessing invalid objects
        except (KeyError, TypeError):
            msg = self._format_msg(1, entity_type=entity_type)
            raise BackendError(msg)

        # If try to create already existing object
        except ValueError:
            msg = self._format_msg(2, entity_type=entity_type, entity_id=entity_id)
            raise BackendError(msg)

    def read_object(self, api: str, **kwargs) -> dict:
        """
        Get an object from local.

        Parameters
        ----------
        api : str
            Read API.

        Returns
        -------
        dict
            The read object.
        """
        if api == LocalClientVar.EMPTY.value:
            return {}
        entity_type, entity_id, context_api = self._parse_api(api)
        if entity_id is None:
            msg = self._format_msg(4)
            raise BackendError(msg)
        try:
            # Base API
            #
            # GET /api/v1/projects/<entity_id>
            #
            # self._parse_api() should return only entity_type

            if not context_api:
                obj = self._db[entity_type][entity_id]

                # If the object is a project, we need to add the project spec,
                # for example artifacts, functions, workflows, etc.
                # Technically we have only projects that access base apis,
                # we check entity_type just in case we add something else.
                if entity_type == "projects":
                    obj = self._get_project_spec(obj, entity_id)
                return obj

            # Context API
            #
            # GET /api/v1/-/<project-name>/runs/<entity_id>
            # GET /api/v1/-/<project-name>/artifacts/<entity_id>
            # GET /api/v1/-/<project-name>/functions/<entity_id>
            #
            # self._parse_api() should return entity_type and entity_id/version

            else:
                for _, v in self._db[entity_type].items():
                    if entity_id in v:
                        return v[entity_id]
                else:
                    raise KeyError

        except KeyError:
            msg = self._format_msg(3, entity_type=entity_type, entity_id=entity_id)
            raise BackendError(msg)

    def update_object(self, api: str, obj: Any, **kwargs) -> dict:
        """
        Update an object in local.

        Parameters
        ----------
        api : str
            Update API.
        obj : dict
            Object to update.

        Returns
        -------
        dict
            The updated object.
        """
        if api == LocalClientVar.EMPTY.value:
            return {}
        if not isinstance(obj, dict):
            raise TypeError("Object must be a dictionary")

        entity_type, entity_id, context_api = self._parse_api(api)
        try:
            # API example
            #
            # PUT /api/v1/projects/<entity_id>

            if not context_api:
                self._db[entity_type][entity_id] = obj

            # Context API
            #
            # PUT /api/v1/-/<project-name>/runs/<entity_id>
            # PUT /api/v1/-/<project-name>/artifacts/<entity_id>

            else:
                name = obj.get("name", entity_id)
                self._db[entity_type][name][entity_id] = obj

        except KeyError:
            msg = self._format_msg(3, entity_type=entity_type, entity_id=entity_id)
            raise BackendError(msg)

        return obj

    def delete_object(self, api: str, **kwargs) -> dict:
        """
        Delete an object from local.

        Parameters
        ----------
        api : str
            Delete API.
        **kwargs : dict
            Keyword arguments parsed from request.

        Returns
        -------
        dict
            Response object.
        """
        entity_type, entity_id, context_api = self._parse_api(api)
        try:
            # Base API
            #
            # DELETE /api/v1/projects/<entity_id>

            if not context_api:
                self._db[entity_type].pop(entity_id)

            # Context API
            #
            # DELETE /api/v1/-/<project-name>/artifacts/<entity_id>
            #
            # We do not handle cascade in local client and
            # in the sdk we selectively delete objects by id,
            # not by name nor entity_type.

            else:
                reset_latest = False

                # Name is optional and extracted from kwargs
                # "params": {"name": <name>}
                name = kwargs.get("params", {}).get("name")

                # Delete by name
                if entity_id is None and name is not None:
                    self._db[entity_type].pop(name, None)
                    return {"deleted": True}

                # Delete by id
                for _, v in self._db[entity_type].items():
                    if entity_id in v:
                        v.pop(entity_id)

                        # Handle latest
                        if v["latest"]["id"] == entity_id:
                            name = v["latest"].get("name", entity_id)
                            v.pop("latest")
                            reset_latest = True
                        break
                else:
                    raise KeyError

                if name is not None:
                    # Pop name if empty
                    if not self._db[entity_type][name]:
                        self._db[entity_type].pop(name)

                    # Handle latest
                    elif reset_latest:
                        latest_uuid = None
                        latest_date = None
                        for k, v in self._db[entity_type][name].items():
                            # Get created from metadata. If tzinfo is None, set it to UTC
                            # If created is not in ISO format, use fallback
                            fallback = datetime.fromtimestamp(0, timezone.utc)
                            try:
                                current_created = datetime.fromisoformat(v.get("metadata", {}).get("created"))
                                if current_created.tzinfo is None:
                                    current_created = current_created.replace(tzinfo=timezone.utc)
                            except ValueError:
                                current_created = fallback

                            # Update latest date and uuid
                            if latest_date is None or current_created > latest_date:
                                latest_uuid = k
                                latest_date = current_created

                        # Set new latest
                        if latest_uuid is not None:
                            self._db[entity_type][name]["latest"] = self._db[entity_type][name][latest_uuid]

        except KeyError:
            msg = self._format_msg(3, entity_type=entity_type, entity_id=entity_id)
            raise BackendError(msg)
        return {"deleted": True}

    def list_objects(self, api: str, **kwargs) -> list:
        """
        List objects.

        Parameters
        ----------
        api : str
            List API.
        **kwargs : dict
            Keyword arguments parsed from request.

        Returns
        -------
        list | None
            The list of objects.
        """
        entity_type, _, _ = self._parse_api(api)

        # Name is optional and extracted from kwargs
        # "params": {"name": <name>}
        name = kwargs.get("params", {}).get("name")
        if name is not None:
            return [self._db[entity_type][name]["latest"]]

        try:
            # If no name is provided, get latest objects
            listed_objects = [v["latest"] for _, v in self._db[entity_type].items()]
        except KeyError:
            listed_objects = []

        # If kind is provided, return objects by kind
        kind = kwargs.get("params", {}).get("kind")
        if kind is not None:
            listed_objects = [obj for obj in listed_objects if obj["kind"] == kind]

        # If function is provided, return objects by function
        spec_params = ["function", "task"]
        for i in spec_params:
            p = kwargs.get("params", {}).get(i)
            if p is not None:
                listed_objects = [obj for obj in listed_objects if obj["spec"][i] == p]

        return listed_objects

    def list_first_object(self, api: str, **kwargs) -> dict:
        """
        List first objects.

        Parameters
        ----------
        api : str
            The api to list the objects with.
        **kwargs : dict
            Keyword arguments passed to the request.

        Returns
        -------
        dict
            The list of objects.
        """
        try:
            return self.list_objects(api, **kwargs)[0]
        except IndexError:
            raise IndexError("No objects found")

    def search_objects(self, api: str, **kwargs) -> dict:
        """
        Search objects from Local.

        Parameters
        ----------
        api : str
            Search API.
        **kwargs : dict
            Keyword arguments to pass to the request.

        Returns
        -------
        dict
            Response objects.
        """
        raise NotImplementedError("Local client does not support search_objects.")

    ##############################
    # Helpers
    ##############################

    def _parse_api(self, api: str) -> tuple:
        """
        Parse the given API to extract the entity_type, entity_id
        and if its a context API.

        Parameters
        ----------
        api : str
            API to parse.

        Returns
        -------
        tuple
            Parsed elements.
        """
        # Remove prefix from API
        api = api.removeprefix("/api/v1/")

        # Set context flag by default to False
        context_api = False

        # Remove context prefix from API and set context flag to True
        if api.startswith("-/"):
            context_api = True
            api = api[2:]

        # Return parsed elements
        return self._parse_api_elements(api, context_api)

    @staticmethod
    def _parse_api_elements(api: str, context_api: bool) -> tuple:
        """
        Parse the elements from the given API.
        Elements returned are: entity_type, entity_id, context_api.

        Parameters
        ----------
        api : str
            Parsed API.
        context_api : bool
            True if the API is a context API.

        Returns
        -------
        tuple
            Parsed elements from the API.
        """
        # Split API path
        parsed = api.split("/")

        # Base API for versioned objects

        # POST /api/v1/<entity_type>
        # Returns entity_type, None, False
        if len(parsed) == 1 and not context_api:
            return parsed[0], None, context_api

        # GET/DELETE/UPDATE /api/v1/<entity_type>/<entity_id>
        # Return entity_type, entity_id, False
        if len(parsed) == 2 and not context_api:
            return parsed[0], parsed[1], context_api

        # Context API for versioned objects

        # POST /api/v1/-/<project>/<entity_type>
        # Returns entity_type, None, True
        if len(parsed) == 2 and context_api:
            return parsed[1], None, context_api

        # GET/DELETE/UPDATE /api/v1/-/<project>/<entity_type>/<entity_id>
        # Return entity_type, entity_id, True
        if len(parsed) == 3 and context_api:
            return parsed[1], parsed[2], context_api

        raise ValueError(f"Invalid API: {api}")

    def _get_project_spec(self, obj: dict, name: str) -> dict:
        """
        Enrich project object with spec (artifacts, functions, etc.).

        Parameters
        ----------
        obj : dict
            The project object.
        name : str
            The project name.

        Returns
        -------
        dict
            The project object with the spec.
        """
        # Deepcopy to avoid modifying the original object
        project = deepcopy(obj)
        spec = project.get("spec", {})

        # Get all entities associated with the project specs
        projects_entities = [k for k, _ in self._db.items() if k not in ["projects", "runs", "tasks"]]

        for entity_type in projects_entities:
            # Get all objects of the entity type for the project
            objs = self._db[entity_type]

            # Set empty list
            spec[entity_type] = []

            # Cycle through named objects
            for _, named_entities in objs.items():
                # Get latest version
                for version, entity in named_entities.items():
                    if version != "latest":
                        continue

                    # Deepcopy to avoid modifying the original object
                    copied = deepcopy(entity)

                    # Remove spec if not embedded
                    if not copied.get("metadata", {}).get("embedded", False):
                        copied.pop("spec", None)

                    # Add to project spec
                    if copied["project"] == name:
                        spec[entity_type].append(copied)

        return project

    ##############################
    # Utils
    ##############################

    @staticmethod
    def _format_msg(
        error_code: int,
        entity_type: str | None = None,
        entity_id: str | None = None,
    ) -> str:
        """
        Format a message.

        Parameters
        ----------
        error_code : int
            Error code identifying the type of error.
        entity_type : str, optional
            Entity type that caused the error.
        entity_id : str, optional
            Entity ID that caused the error.

        Returns
        -------
        str
            The formatted error message.
        """
        msg = {
            1: f"Object '{entity_type}' to create is not valid",
            2: f"Object '{entity_type}' with id '{entity_id}' already exists",
            3: f"Object '{entity_type}' with id '{entity_id}' not found",
            4: "Must provide entity_id to read an object",
        }
        return msg[error_code]

    ##############################
    # Interface methods
    ##############################

    @staticmethod
    def is_local() -> bool:
        """
        Declare if Client is local.

        Returns
        -------
        bool
            True
        """
        return True
