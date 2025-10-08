# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing
from typing import Any
from warnings import warn

from requests import request
from requests.exceptions import JSONDecodeError

from digitalhub.stores.client._base.client import Client
from digitalhub.stores.client.dhcore.api_builder import ClientDHCoreApiBuilder
from digitalhub.stores.client.dhcore.configurator import ClientDHCoreConfigurator
from digitalhub.stores.client.dhcore.error_parser import ErrorParser
from digitalhub.stores.client.dhcore.key_builder import ClientDHCoreKeyBuilder
from digitalhub.stores.client.dhcore.params_builder import ClientDHCoreParametersBuilder
from digitalhub.utils.exceptions import BackendError, ClientError
from digitalhub.utils.generic_utils import dump_json

if typing.TYPE_CHECKING:
    from requests import Response


# API levels that are supported
MAX_API_LEVEL = 20
MIN_API_LEVEL = 13
LIB_VERSION = 13


class ClientDHCore(Client):
    """
    DHCore client for remote DigitalHub Core backend communication.

    The DHCore client is used to communicate with the DigitalHub Core
    backend API via REST. The client supports multiple authentication methods:
    - Basic authentication (username/password)
    - OAuth2 token authentication with automatic token refresh
    - Personal access token exchange

    At initialization, the client attempts to load endpoint and authentication
    parameters from environment variables and the .dhcore configuration file.
    If authentication or endpoint errors occur during client creation, users
    can update the configuration using the `set_dhcore_env` function from
    the utils module.

    The client automatically handles:
    - API version compatibility checking
    - Pagination for list operations
    - Token refresh on authentication errors
    - Error parsing and exception mapping
    - JSON serialization/deserialization

    Parameters
    ----------
    config : dict, optional
        DHCore environment configuration. If None, configuration will
        be loaded from environment variables and configuration files.

    Attributes
    ----------
    _api_builder : ClientDHCoreApiBuilder
        Builds API endpoint URLs for different operations.
    _key_builder : ClientDHCoreKeyBuilder
        Builds storage keys for entities.
    _params_builder : ClientDHCoreParametersBuilder
        Builds request parameters for API calls.
    _error_parser : ErrorParser
        Parses backend responses and raises appropriate exceptions.
    _configurator : ClientDHCoreConfigurator
        Manages client configuration and authentication.

    Notes
    -----
    Supported DHCore API versions: {MIN_API_LEVEL} to {MAX_API_LEVEL}
    Current library API version: {LIB_VERSION}

    Examples
    --------
    >>> from digitalhub.stores.client.api import get_client
    >>> client = get_client(local=False)
    >>> # Client is now ready for API operations
    """

    def __init__(self, config: dict | None = None) -> None:
        """
        Initialize DHCore client.

        Creates a new DHCore client instance with all necessary components
        for communicating with the DigitalHub Core backend. Sets up API
        builders, configurators, and error handling.

        Parameters
        ----------
        config : dict, optional
            DHCore environment configuration. If None, configuration will
            be loaded from environment variables and configuration files.

        Returns
        -------
        None
        """
        super().__init__()

        # API builder
        self._api_builder = ClientDHCoreApiBuilder()

        # Key builder
        self._key_builder = ClientDHCoreKeyBuilder()

        # Parameters builder
        self._params_builder = ClientDHCoreParametersBuilder()

        # Error parser
        self._error_parser = ErrorParser()

        # Client Configurator
        self._configurator = ClientDHCoreConfigurator()

    ##############################
    # CRUD methods
    ##############################

    def create_object(self, api: str, obj: Any, **kwargs) -> dict:
        """
        Create an object in DHCore.

        Sends a POST request to the DHCore backend to create a new object.
        Automatically sets the appropriate Content-Type header and serializes
        the object to JSON format.

        Parameters
        ----------
        api : str
            The API endpoint path for creating the object.
        obj : Any
            The object to create. Will be serialized to JSON.
        **kwargs : dict
            Additional keyword arguments to pass to the HTTP request,
            such as headers, params, etc.

        Returns
        -------
        dict
            The created object as returned by the backend.

        Raises
        ------
        BackendError
            If the backend returns an error response.
        ClientError
            If there are client-side configuration issues.
        """
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["Content-Type"] = "application/json"
        kwargs["data"] = dump_json(obj)
        return self._prepare_call("POST", api, **kwargs)

    def read_object(self, api: str, **kwargs) -> dict:
        """
        Get an object from DHCore.

        Sends a GET request to the DHCore backend to retrieve an existing object.

        Parameters
        ----------
        api : str
            The API endpoint path for reading the object.
        **kwargs : dict
            Additional keyword arguments to pass to the HTTP request,
            such as headers, params, etc.

        Returns
        -------
        dict
            The retrieved object as returned by the backend.

        Raises
        ------
        BackendError
            If the backend returns an error response.
        EntityNotExistsError
            If the requested object does not exist.
        """
        return self._prepare_call("GET", api, **kwargs)

    def update_object(self, api: str, obj: Any, **kwargs) -> dict:
        """
        Update an object in DHCore.

        Sends a PUT request to the DHCore backend to update an existing object.
        Automatically sets the appropriate Content-Type header and serializes
        the object to JSON format.

        Parameters
        ----------
        api : str
            The API endpoint path for updating the object.
        obj : Any
            The updated object data. Will be serialized to JSON.
        **kwargs : dict
            Additional keyword arguments to pass to the HTTP request,
            such as headers, params, etc.

        Returns
        -------
        dict
            The updated object as returned by the backend.

        Raises
        ------
        BackendError
            If the backend returns an error response.
        EntityNotExistsError
            If the object to update does not exist.
        """
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["Content-Type"] = "application/json"
        kwargs["data"] = dump_json(obj)
        return self._prepare_call("PUT", api, **kwargs)

    def delete_object(self, api: str, **kwargs) -> dict:
        """
        Delete an object from DHCore.

        Sends a DELETE request to the DHCore backend to remove an object.
        If the backend returns a boolean response, it will be wrapped in
        a dictionary with a "deleted" key.

        Parameters
        ----------
        api : str
            The API endpoint path for deleting the object.
        **kwargs : dict
            Additional keyword arguments to pass to the HTTP request,
            such as headers, params, cascade options, etc.

        Returns
        -------
        dict
            The deletion result. Either the backend response or
            {"deleted": True/False} if backend returns a boolean.

        Raises
        ------
        BackendError
            If the backend returns an error response.
        EntityNotExistsError
            If the object to delete does not exist.
        """
        resp = self._prepare_call("DELETE", api, **kwargs)
        if isinstance(resp, bool):
            resp = {"deleted": resp}
        return resp

    def list_objects(self, api: str, **kwargs) -> list[dict]:
        """
        List objects from DHCore.

        Sends GET requests to the DHCore backend to retrieve a paginated list
        of objects. Automatically handles pagination by making multiple requests
        until all objects are retrieved.

        Parameters
        ----------
        api : str
            The API endpoint path for listing objects.
        **kwargs : dict
            Additional keyword arguments to pass to the HTTP request.
            Can include 'params' dict with pagination parameters.

        Returns
        -------
        list[dict]
            A list containing all objects from all pages.

        Raises
        ------
        BackendError
            If the backend returns an error response.

        Notes
        -----
        This method automatically handles pagination starting from page 0
        and continues until all pages are retrieved.
        """
        if "params" not in kwargs:
            kwargs["params"] = {}

        start_page = 0
        if "page" not in kwargs["params"]:
            kwargs["params"]["page"] = start_page

        objects = []
        while True:
            resp = self._prepare_call("GET", api, **kwargs)
            contents = resp["content"]
            total_pages = resp["totalPages"]
            if not contents or kwargs["params"]["page"] >= total_pages:
                break
            objects.extend(contents)
            kwargs["params"]["page"] += 1

        return objects

    def list_first_object(self, api: str, **kwargs) -> dict:
        """
        Get the first object from a list in DHCore.

        Retrieves the first object from a paginated list by calling
        list_objects and returning the first item.

        Parameters
        ----------
        api : str
            The API endpoint path for listing objects.
        **kwargs : dict
            Additional keyword arguments to pass to the HTTP request.

        Returns
        -------
        dict
            The first object from the list.

        Raises
        ------
        BackendError
            If no objects are found or if the backend returns an error.
        """
        try:
            return self.list_objects(api, **kwargs)[0]
        except IndexError:
            raise BackendError("No object found.")

    def search_objects(self, api: str, **kwargs) -> list[dict]:
        """
        Search objects from DHCore.

        Performs a search query against the DHCore backend using Solr search
        capabilities. Handles pagination and removes search highlights from
        the returned objects.

        Parameters
        ----------
        api : str
            The API endpoint path for searching objects (usually Solr search).
        **kwargs : dict
            Additional keyword arguments to pass to the HTTP request.
            Can include search parameters, filters, pagination options, etc.

        Returns
        -------
        list[dict]
            A list of objects matching the search criteria, with search
            highlights removed.

        Raises
        ------
        BackendError
            If the backend returns an error response.

        Notes
        -----
        This method sets default values for pagination (page=0, size=10)
        and sorting (by metadata.updated descending) if not provided.
        Search highlights are automatically removed from results.
        """
        if "params" not in kwargs:
            kwargs["params"] = {}

        start_page = 0
        if "page" not in kwargs["params"]:
            kwargs["params"]["page"] = start_page

        if "size" not in kwargs["params"]:
            kwargs["params"]["size"] = 10

        # Add sorting
        if "sort" not in kwargs["params"]:
            kwargs["params"]["sort"] = "metadata.updated,DESC"

        objects_with_highlights: list[dict] = []
        while True:
            resp = self._prepare_call("GET", api, **kwargs)
            contents = resp["content"]
            total_pages = resp["totalPages"]
            if not contents or kwargs["params"]["page"] >= total_pages:
                break
            objects_with_highlights.extend(contents)
            kwargs["params"]["page"] += 1

        objects = []
        for obj in objects_with_highlights:
            obj.pop("highlights", None)
            objects.append(obj)

        return objects

    ##############################
    # Call methods
    ##############################

    def _prepare_call(self, call_type: str, api: str, **kwargs) -> dict:
        """
        Prepare a call to the DHCore API.

        Handles the preparation of an API call by checking configuration,
        building the URL, and adding authentication parameters.

        Parameters
        ----------
        call_type : str
            The HTTP method type (GET, POST, PUT, DELETE, etc.).
        api : str
            The API endpoint path to call.
        **kwargs : dict
            Additional keyword arguments to pass to the HTTP request.

        Returns
        -------
        dict
            The response from the API call.

        Raises
        ------
        ClientError
            If the client configuration is invalid.
        BackendError
            If the backend returns an error response.
        """
        self._configurator.check_config()
        url = self._build_url(api)
        full_kwargs = self._configurator.get_auth_parameters(kwargs)
        return self._make_call(call_type, url, **full_kwargs)

    def _build_url(self, api: str) -> str:
        """
        Build the complete URL for an API call.

        Combines the configured endpoint with the API path to create
        the full URL for the HTTP request.

        Parameters
        ----------
        api : str
            The API endpoint path. Leading slashes are automatically handled.

        Returns
        -------
        str
            The complete URL for the API call.

        Notes
        -----
        This method automatically removes leading slashes from the API path
        to ensure proper URL construction.
        """
        endpoint = self._configurator.get_endpoint()
        return f"{endpoint}/{api.removeprefix('/')}"

    def _make_call(self, call_type: str, url: str, refresh: bool = True, **kwargs) -> dict:
        """
        Make a call to the DHCore API.

        Executes the actual HTTP request to the DHCore backend, handles
        API version checking, automatic token refresh on 401 errors,
        and error parsing.

        Parameters
        ----------
        call_type : str
            The HTTP method type (GET, POST, PUT, DELETE, etc.).
        url : str
            The complete URL to call.
        refresh : bool, default True
            Whether to attempt token refresh on authentication errors.
            Set to False to prevent infinite recursion during refresh.
        **kwargs : dict
            Additional keyword arguments to pass to the HTTP request.

        Returns
        -------
        dict
            The parsed response from the backend as a dictionary.

        Raises
        ------
        ClientError
            If the backend API version is not supported.
        BackendError
            If the backend returns an error response or response parsing fails.
        UnauthorizedError
            If authentication fails and token refresh is not possible.

        Notes
        -----
        This method automatically handles:
        - API version compatibility checking
        - OAuth2 token refresh on 401 errors
        - Response parsing and error handling
        - 60-second timeout for all requests
        """
        # Call the API
        response = request(call_type, url, timeout=60, **kwargs)

        # Evaluate DHCore API version
        self._check_core_version(response)

        # Handle token refresh (redo call)
        if (response.status_code in [401]) and (refresh) and self._configurator.refreshable_auth_types():
            self._configurator.refresh_credentials(change_origin=True)
            kwargs = self._configurator.get_auth_parameters(kwargs)
            return self._make_call(call_type, url, refresh=False, **kwargs)

        self._error_parser.parse(response)
        return self._dictify_response(response)

    def _check_core_version(self, response: Response) -> None:
        """
        Check DHCore API version compatibility.

        Validates that the DHCore backend API version is compatible with
        this client library. Issues warnings if the backend version is
        newer than the library version.

        Parameters
        ----------
        response : Response
            The HTTP response object containing the X-Api-Level header.

        Returns
        -------
        None

        Raises
        ------
        ClientError
            If the backend API level is not supported by this client.

        Notes
        -----
        Supported API levels: {MIN_API_LEVEL} to {MAX_API_LEVEL}
        Current library version: {LIB_VERSION}
        """
        if "X-Api-Level" in response.headers:
            core_api_level = int(response.headers["X-Api-Level"])
            if not (MIN_API_LEVEL <= core_api_level <= MAX_API_LEVEL):
                raise ClientError("Backend API level not supported.")
            if LIB_VERSION < core_api_level:
                warn("Backend API level is higher than library version. You should consider updating the library.")

    def _dictify_response(self, response: Response) -> dict:
        """
        Parse HTTP response to dictionary.

        Converts the HTTP response body from JSON to a Python dictionary.
        Handles empty responses gracefully.

        Parameters
        ----------
        response : Response
            The HTTP response object to parse.

        Returns
        -------
        dict
            The parsed response body as a dictionary. Returns empty dict
            if response body is empty.

        Raises
        ------
        BackendError
            If the response cannot be parsed as JSON.

        Notes
        -----
        Empty response bodies are treated as valid and return an empty dict.
        """
        try:
            return response.json()
        except JSONDecodeError:
            if response.text == "":
                return {}
            raise BackendError("Backend response could not be parsed.")

    ##############################
    # Interface methods
    ##############################

    @staticmethod
    def is_local() -> bool:
        """
        Check if this client operates locally.

        Returns a flag indicating whether this client instance operates
        on local data or communicates with a remote backend.

        Returns
        -------
        bool
            False, indicating this client communicates with a remote
            DHCore backend, not local storage.

        Notes
        -----
        This method is used to distinguish between ClientDHCore (returns False)
        and ClientLocal (returns True) implementations.
        """
        return False
