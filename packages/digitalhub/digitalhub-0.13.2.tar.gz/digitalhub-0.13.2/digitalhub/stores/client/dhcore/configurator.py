# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing

from requests import request

from digitalhub.stores.client.dhcore.enums import AuthType
from digitalhub.stores.credentials.configurator import Configurator
from digitalhub.stores.credentials.enums import CredsEnvVar
from digitalhub.stores.credentials.handler import creds_handler
from digitalhub.utils.exceptions import ClientError
from digitalhub.utils.generic_utils import list_enum
from digitalhub.utils.uri_utils import has_remote_scheme

if typing.TYPE_CHECKING:
    from requests import Response


class ClientDHCoreConfigurator(Configurator):
    """
    Configurator object used to configure the client.

    The configurator starts reading the credentials from the
    environment and from the ini file and stores them into the
    creds_handler object.

    While reading the credentials from the two sources (environment and file),
    the configurator evaluate if the required keys are present in both sources.
    If the required keys are not present in both sources, the configurator
    will rise an error, otherwise decide which source to use.

    Once the credentials are read, the configurator check the current profile
    name from the ini file, and set it. The default one is __default. The
    profile is used to discriminate a set of credentials inside the ini file.

    The configurator finally set the authentication type based on the credentials.
    The logic is the following:

        1. Check for a personal access token. Use it immediately to
           require a timed access token in an exchange endpoint.
           Switche then the origin to file and .
           Set the auth type to EXCHANGE.
        2. Check for an access token and a refresh token.
           Set the auth type to OAUTH2.
        3. Check for username and password.
           Set the auth type to BASIC.
        4. If none of the above is true, leave the auth type to None.
    """

    keys = [*list_enum(CredsEnvVar)]
    required_keys = [CredsEnvVar.DHCORE_ENDPOINT.value]
    keys_to_unprefix = [
        CredsEnvVar.DHCORE_REFRESH_TOKEN.value,
        CredsEnvVar.DHCORE_ACCESS_TOKEN.value,
        CredsEnvVar.DHCORE_ISSUER.value,
        CredsEnvVar.DHCORE_CLIENT_ID.value,
    ]

    def __init__(self) -> None:
        """
        Initialize the DHCore configurator.

        Sets up the configurator by calling the parent constructor and
        initializing the authentication type evaluation process.

        Returns
        -------
        None
        """
        super().__init__()
        self._auth_type: str | None = None
        self.set_auth_type()

    ##############################
    # Credentials methods
    ##############################

    def load_env_vars(self) -> None:
        """
        Load credentials from environment variables.

        Retrieves DHCore credentials from environment variables, sanitizes
        them (particularly endpoint URLs), and stores them in the credentials
        handler for the environment origin.

        Returns
        -------
        None

        Notes
        -----
        This method sanitizes endpoint and issuer URLs to ensure they have
        proper schemes and removes trailing slashes.
        """
        env_creds = self._creds_handler.load_from_env(self.keys)
        env_creds = self._sanitize_env_vars(env_creds)
        self._creds_handler.set_credentials(self._env, env_creds)

    def _sanitize_env_vars(self, creds: dict) -> dict:
        """
        Sanitize credentials loaded from environment variables.

        Validates and normalizes endpoint and issuer URLs from environment
        variables. Ensures URLs have proper schemes and removes trailing slashes.

        Parameters
        ----------
        creds : dict
            Raw credentials dictionary loaded from environment variables.

        Returns
        -------
        dict
            Sanitized credentials dictionary with normalized URLs.

        Raises
        ------
        ClientError
            If endpoint or issuer URLs have invalid schemes.

        Notes
        -----
        Environment variables are expected to have the full "DHCORE_" prefix
        for issuer endpoints.
        """
        creds[CredsEnvVar.DHCORE_ENDPOINT.value] = self._sanitize_endpoint(creds[CredsEnvVar.DHCORE_ENDPOINT.value])
        creds[CredsEnvVar.DHCORE_ISSUER.value] = self._sanitize_endpoint(creds[CredsEnvVar.DHCORE_ISSUER.value])
        return creds

    def load_file_vars(self) -> None:
        """
        Load credentials from configuration file.

        Retrieves DHCore credentials from the .dhcore.ini file, handles
        compatibility with CLI format (keys without DHCORE_ prefix), and
        falls back to environment variables for missing endpoint and
        personal access token values.

        Returns
        -------
        None

        Notes
        -----
        This method handles the case where:
        - Endpoint might not be present in file response, falls back to env
        - Personal access token might not be present, falls back to env
        - File format uses keys without "DHCORE_" prefix for compatibility
        """
        keys = [*self._remove_prefix_dhcore()]
        file_creds = self._creds_handler.load_from_file(keys)
        env_creds = self._creds_handler.load_from_env(self.keys)

        # Because in the response there is no endpoint
        if file_creds[CredsEnvVar.DHCORE_ENDPOINT.value] is None:
            file_creds[CredsEnvVar.DHCORE_ENDPOINT.value] = env_creds.get(CredsEnvVar.DHCORE_ENDPOINT.value)

        # Because in the response there is no personal access token
        if file_creds[CredsEnvVar.DHCORE_PERSONAL_ACCESS_TOKEN.value] is None:
            file_creds[CredsEnvVar.DHCORE_PERSONAL_ACCESS_TOKEN.value] = env_creds.get(
                CredsEnvVar.DHCORE_PERSONAL_ACCESS_TOKEN.value
            )

        file_creds = self._sanitize_file_vars(file_creds)
        self._creds_handler.set_credentials(self._file, file_creds)

    def _sanitize_file_vars(self, creds: dict) -> dict:
        """
        Sanitize credentials loaded from configuration file.

        Handles the different key formats used in configuration files compared
        to environment variables. File format omits "DHCORE_" prefix for
        certain keys for CLI compatibility.

        Parameters
        ----------
        creds : dict
            Raw credentials dictionary loaded from configuration file.

        Returns
        -------
        dict
            Sanitized credentials dictionary with standardized key names
            and normalized URLs, filtered to include only valid keys.

        Raises
        ------
        ClientError
            If endpoint or issuer URLs have invalid schemes.

        Notes
        -----
        File format expects these keys without "DHCORE_" prefix:
        - issuer, client_id, access_token, refresh_token
        But uses full names for: endpoint, user, password, personal_access_token
        """
        creds[CredsEnvVar.DHCORE_ENDPOINT.value] = self._sanitize_endpoint(creds[CredsEnvVar.DHCORE_ENDPOINT.value])
        creds[CredsEnvVar.DHCORE_ISSUER.value] = self._sanitize_endpoint(
            creds[CredsEnvVar.DHCORE_ISSUER.value.removeprefix("DHCORE_")]
        )
        creds[CredsEnvVar.DHCORE_REFRESH_TOKEN.value] = creds[
            CredsEnvVar.DHCORE_REFRESH_TOKEN.value.removeprefix("DHCORE_")
        ]
        creds[CredsEnvVar.DHCORE_ACCESS_TOKEN.value] = creds[
            CredsEnvVar.DHCORE_ACCESS_TOKEN.value.removeprefix("DHCORE_")
        ]
        creds[CredsEnvVar.DHCORE_CLIENT_ID.value] = creds[CredsEnvVar.DHCORE_CLIENT_ID.value.removeprefix("DHCORE_")]
        return {k: v for k, v in creds.items() if k in self.keys}

    @staticmethod
    def _sanitize_endpoint(endpoint: str | None = None) -> str | None:
        """
        Sanitize and validate endpoint URL.

        Validates that the endpoint URL has a proper HTTP/HTTPS scheme,
        trims whitespace, and removes trailing slashes for consistency.

        Parameters
        ----------
        endpoint : str, optional
            The endpoint URL to sanitize. If None, returns None.

        Returns
        -------
        str or None
            The sanitized endpoint URL with trailing slash removed,
            or None if input was None.

        Raises
        ------
        ClientError
            If the endpoint does not start with http:// or https://.

        Notes
        -----
        This method ensures endpoint URLs are properly formatted for
        HTTP requests and prevents common URL formatting issues.
        """
        if endpoint is None:
            return
        if not has_remote_scheme(endpoint):
            raise ClientError("Invalid endpoint scheme. Must start with http:// or https://.")

        endpoint = endpoint.strip()
        return endpoint.removesuffix("/")

    def get_endpoint(self) -> str:
        """
        Get the configured DHCore backend endpoint.

        Retrieves the DHCore endpoint URL from the current credential source
        (environment or file based on current origin).

        Returns
        -------
        str
            The DHCore backend endpoint URL.

        Raises
        ------
        KeyError
            If the endpoint is not configured in the current credential source.

        Notes
        -----
        The endpoint returned is already sanitized and validated during
        the credential loading process.
        """
        creds = self._creds_handler.get_credentials(self._origin)
        return creds[CredsEnvVar.DHCORE_ENDPOINT.value]

    ##############################
    # Origin methods
    ##############################

    def change_origin(self) -> None:
        """
        Change the credentials origin and re-evaluate authentication type.

        Switches the credential source (between environment and file) and
        re-evaluates the authentication type based on the new credential set.
        This is typically called when the current credential source fails
        or when switching contexts.

        Returns
        -------
        None

        Notes
        -----
        This method extends the parent class behavior by also re-evaluating
        the authentication type, which may change based on different
        credentials available in the new source.
        """
        super().change_origin()

        # Re-evaluate the auth type
        self.set_auth_type()

    ##############################
    # Auth methods
    ##############################

    def set_auth_type(self) -> None:
        """
        Evaluate and set the authentication type from available credentials.

        Analyzes the available credentials and determines the appropriate
        authentication method based on the following priority:
        1. EXCHANGE - Personal access token available
        2. OAUTH2 - Access token and refresh token available
        3. ACCESS_TOKEN - Only access token available
        4. BASIC - Username and password available
        5. None - No valid credentials found

        For EXCHANGE authentication, automatically performs token exchange
        and switches to file-based credential storage.

        Returns
        -------
        None

        Notes
        -----
        When EXCHANGE authentication is detected, this method automatically:
        - Performs credential refresh to exchange the personal access token
        - Changes origin to file-based storage for the new tokens
        - Updates the authentication type accordingly
        """
        creds = creds_handler.get_credentials(self._origin)
        self._auth_type = self._eval_auth_type(creds)
        # If we have an exchange token, we need to get a new access token.
        # Therefore, we change the origin to file, where the refresh token is written.
        # We also try to fetch the PAT from both env and file
        if self._auth_type == AuthType.EXCHANGE.value:
            self.refresh_credentials(change_origin=True)
            # Just to ensure we get the right source from file
            self.change_to_file()

    def refreshable_auth_types(self) -> bool:
        """
        Check if the current authentication type supports token refresh.

        Determines whether the current authentication method supports
        automatic token refresh capabilities.

        Returns
        -------
        bool
            True if the authentication type supports refresh (OAUTH2 or EXCHANGE),
            False otherwise (BASIC or ACCESS_TOKEN).

        Notes
        -----
        Only OAUTH2 and EXCHANGE authentication types support refresh:
        - OAUTH2: Uses refresh token to get new access tokens
        - EXCHANGE: Uses personal access token for token exchange
        - BASIC and ACCESS_TOKEN do not support refresh
        """
        return self._auth_type in [AuthType.OAUTH2.value, AuthType.EXCHANGE.value]

    def get_auth_parameters(self, kwargs: dict) -> dict:
        """
        Add authentication parameters to HTTP request arguments.

        Modifies the provided kwargs dictionary to include the appropriate
        authentication headers or parameters based on the current authentication
        type and available credentials.

        Parameters
        ----------
        kwargs : dict
            HTTP request keyword arguments to be modified with authentication.

        Returns
        -------
        dict
            The modified kwargs dictionary with authentication parameters added.

        Notes
        -----
        Authentication is added based on auth type:
        - OAUTH2/EXCHANGE/ACCESS_TOKEN: Adds Authorization Bearer header
        - BASIC: Adds auth tuple with username/password
        - None: No authentication added

        The method assumes that:
        - Authentication type has been properly set
        - For EXCHANGE type, refresh token has been obtained
        - Required credentials are available for the current auth type
        """
        creds = creds_handler.get_credentials(self._origin)
        if self._auth_type in (
            AuthType.EXCHANGE.value,
            AuthType.OAUTH2.value,
            AuthType.ACCESS_TOKEN.value,
        ):
            access_token = creds[CredsEnvVar.DHCORE_ACCESS_TOKEN.value]
            if "headers" not in kwargs:
                kwargs["headers"] = {}
            kwargs["headers"]["Authorization"] = f"Bearer {access_token}"
        elif self._auth_type == AuthType.BASIC.value:
            user = creds[CredsEnvVar.DHCORE_USER.value]
            password = creds[CredsEnvVar.DHCORE_PASSWORD.value]
            kwargs["auth"] = (user, password)
        return kwargs

    def refresh_credentials(self, change_origin: bool = False) -> None:
        """
        Refresh authentication credentials by obtaining new access tokens.

        Performs credential refresh using either OAuth2 refresh token flow
        or personal access token exchange, depending on the current
        authentication type. Updates stored credentials with new tokens.

        Parameters
        ----------
        change_origin : bool, default False
            Whether to allow changing credential source if refresh fails.
            If True and refresh fails, attempts to switch credential sources
            and retry once.

        Returns
        -------
        None

        Raises
        ------
        ClientError
            If the authentication type doesn't support refresh, if required
            credentials are missing, or if refresh fails and change_origin
            is False.

        Notes
        -----
        Refresh behavior by authentication type:
        - OAUTH2: Uses refresh_token grant to get new access/refresh tokens
        - EXCHANGE: Uses token exchange with personal access token

        If refresh fails with 400/401/403 status and change_origin=True,
        attempts to switch credential sources and retry once.

        New credentials are automatically saved to the configuration file
        and the origin is switched to file-based storage.
        """
        if not self.refreshable_auth_types():
            raise ClientError(f"Auth type {self._auth_type} does not support refresh.")

        # Get refresh endpoint
        url = self._get_refresh_endpoint()

        # Get credentials
        creds = self._creds_handler.get_credentials(self._origin)

        # Get client id
        if (client_id := creds.get(CredsEnvVar.DHCORE_CLIENT_ID.value)) is None:
            raise ClientError("Client id not set.")

        # Handling of token exchange or refresh
        if self._auth_type == AuthType.OAUTH2.value:
            response = self._call_refresh_endpoint(
                url,
                client_id=client_id,
                refresh_token=creds.get(CredsEnvVar.DHCORE_REFRESH_TOKEN.value),
                grant_type="refresh_token",
                scope="credentials",
            )
        elif self._auth_type == AuthType.EXCHANGE.value:
            response = self._call_refresh_endpoint(
                url,
                client_id=client_id,
                subject_token=creds.get(CredsEnvVar.DHCORE_PERSONAL_ACCESS_TOKEN.value),
                subject_token_type="urn:ietf:params:oauth:token-type:pat",
                grant_type="urn:ietf:params:oauth:grant-type:token-exchange",
                scope="credentials",
            )

        # Change origin of creds if needed
        if response.status_code in (400, 401, 403):
            if not change_origin:
                raise ClientError("Unable to refresh credentials. Please check your credentials.")
            self.eval_change_origin()
            self.refresh_credentials(change_origin=False)

        response.raise_for_status()

        # Read new credentials and propagate to config file
        self._export_new_creds(response.json())

    def _remove_prefix_dhcore(self) -> list[str]:
        """
        Remove DHCORE_ prefix from selected credential keys for CLI compatibility.

        Creates a list of credential key names with "DHCORE_" prefix removed
        from specific keys that are stored without the prefix in configuration
        files for compatibility with CLI tools.

        Returns
        -------
        list[str]
            List of credential keys with selective prefix removal applied.

        Notes
        -----
        Keys that have prefix removed (defined in keys_to_unprefix):
        - DHCORE_REFRESH_TOKEN -> refresh_token
        - DHCORE_ACCESS_TOKEN -> access_token
        - DHCORE_ISSUER -> issuer
        - DHCORE_CLIENT_ID -> client_id

        Other keys retain their full names for consistency.
        """
        new_list = []
        for key in self.keys:
            if key in self.keys_to_unprefix:
                new_list.append(key.removeprefix("DHCORE_"))
            else:
                new_list.append(key)
        return new_list

    def _get_refresh_endpoint(self) -> str:
        """
        Discover the OAuth2 token refresh endpoint from the issuer.

        Queries the OAuth2 issuer's well-known configuration endpoint to
        discover the token endpoint used for credential refresh operations.

        Returns
        -------
        str
            The token endpoint URL for credential refresh.

        Raises
        ------
        ClientError
            If the issuer endpoint is not configured.
        HTTPError
            If the well-known configuration endpoint is not accessible.
        KeyError
            If the token_endpoint is not found in the issuer configuration.

        Notes
        -----
        This method follows the OAuth2/OpenID Connect discovery standard by:
        1. Accessing the issuer's /.well-known/openid-configuration endpoint
        2. Extracting the token_endpoint from the configuration
        3. Using this endpoint for subsequent token refresh operations
        """
        # Get issuer endpoint
        creds = self._creds_handler.get_credentials(self._origin)
        endpoint_issuer = creds.get(CredsEnvVar.DHCORE_ISSUER.value)
        if endpoint_issuer is None:
            raise ClientError("Issuer endpoint not set.")

        # Standard issuer endpoint path
        url = endpoint_issuer + "/.well-known/openid-configuration"

        # Call issuer to get refresh endpoint
        r = request("GET", url, timeout=60)
        r.raise_for_status()
        return r.json().get("token_endpoint")

    def _call_refresh_endpoint(
        self,
        url: str,
        **kwargs,
    ) -> Response:
        """
        Make HTTP request to OAuth2 token refresh endpoint.

        Performs a POST request to the OAuth2 token endpoint with the
        appropriate form-encoded payload for token refresh or exchange.

        Parameters
        ----------
        url : str
            The token endpoint URL to call.
        **kwargs : dict
            Token request parameters such as grant_type, client_id,
            refresh_token, subject_token, etc.

        Returns
        -------
        Response
            The HTTP response object from the token endpoint.

        Notes
        -----
        This method:
        - Uses application/x-www-form-urlencoded content type as required by OAuth2
        - Sets a 60-second timeout for the request
        - Returns the raw response for caller to handle status and parsing
        """
        # Send request to get new access token
        payload = {**kwargs}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        return request("POST", url, data=payload, headers=headers, timeout=60)

    def _eval_auth_type(self, creds: dict) -> str | None:
        """
        Evaluate authentication type based on available credentials.

        Analyzes the provided credentials and determines the most appropriate
        authentication method based on which credential types are available.

        Parameters
        ----------
        creds : dict
            Dictionary containing credential values.

        Returns
        -------
        str or None
            The determined authentication type from AuthType enum, or None
            if no valid authentication method can be determined.

        Notes
        -----
        Authentication type priority (checked in order):
        1. EXCHANGE - Personal access token is available
        2. OAUTH2 - Both access token and refresh token are available
        3. ACCESS_TOKEN - Only access token is available
        4. BASIC - Both username and password are available
        5. None - No valid credential combination found
        """
        if creds[CredsEnvVar.DHCORE_PERSONAL_ACCESS_TOKEN.value] is not None:
            return AuthType.EXCHANGE.value
        if (
            creds[CredsEnvVar.DHCORE_ACCESS_TOKEN.value] is not None
            and creds[CredsEnvVar.DHCORE_REFRESH_TOKEN.value] is not None
        ):
            return AuthType.OAUTH2.value
        if creds[CredsEnvVar.DHCORE_ACCESS_TOKEN.value] is not None:
            return AuthType.ACCESS_TOKEN.value
        if creds[CredsEnvVar.DHCORE_USER.value] is not None and creds[CredsEnvVar.DHCORE_PASSWORD.value] is not None:
            return AuthType.BASIC.value
        return None

    def _export_new_creds(self, response: dict) -> None:
        """
        Save new credentials from token refresh response.

        Takes the response from a successful token refresh operation and
        persists the new credentials to the configuration file, then
        reloads file-based credentials and switches to file origin.

        Parameters
        ----------
        response : dict
            Token response containing new access_token, refresh_token,
            and other credential information.

        Returns
        -------
        None

        Notes
        -----
        This method:
        1. Writes new credentials to the configuration file
        2. Reloads file-based credentials to ensure consistency
        3. Changes current origin to file since new tokens are file-based

        The response typically contains access_token, refresh_token,
        token_type, expires_in, and other OAuth2 standard fields.
        """
        creds_handler.write_env(response)
        self.load_file_vars()

        # Change current origin to file because of refresh
        self.change_to_file()
