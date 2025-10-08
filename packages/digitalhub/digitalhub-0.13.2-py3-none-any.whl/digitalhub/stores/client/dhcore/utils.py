# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
import typing

from digitalhub.stores.client.api import get_client
from digitalhub.stores.credentials.enums import CredsEnvVar

if typing.TYPE_CHECKING:
    from digitalhub.stores.client.dhcore.client import ClientDHCore


def set_dhcore_env(
    endpoint: str | None = None,
    user: str | None = None,
    password: str | None = None,
    access_token: str | None = None,
    refresh_token: str | None = None,
    client_id: str | None = None,
) -> None:
    """
    Function to set environment variables for DHCore config.

    Sets the environment variables for DHCore configuration and
    reloads the client configurator to use the new settings.
    Note that if the environment variable is already set, it
    will be overwritten.

    Parameters
    ----------
    endpoint : str, optional
        The endpoint URL of the DHCore backend.
    user : str, optional
        The username for basic authentication.
    password : str, optional
        The password for basic authentication.
    access_token : str, optional
        The OAuth2 access token.
    refresh_token : str, optional
        The OAuth2 refresh token.
    client_id : str, optional
        The OAuth2 client identifier.

    Returns
    -------
    None

    Notes
    -----
    After setting the environment variables, this function automatically
    reloads the client configurator to apply the new configuration.
    """
    if endpoint is not None:
        os.environ[CredsEnvVar.DHCORE_ENDPOINT.value] = endpoint
    if user is not None:
        os.environ[CredsEnvVar.DHCORE_USER.value] = user
    if password is not None:
        os.environ[CredsEnvVar.DHCORE_PASSWORD.value] = password
    if access_token is not None:
        os.environ[CredsEnvVar.DHCORE_ACCESS_TOKEN.value] = access_token
    if refresh_token is not None:
        os.environ[CredsEnvVar.DHCORE_REFRESH_TOKEN.value] = refresh_token
    if client_id is not None:
        os.environ[CredsEnvVar.DHCORE_CLIENT_ID.value] = client_id

    client: ClientDHCore = get_client(local=False)
    client._configurator.load_env_vars()


def refresh_token() -> None:
    """
    Function to refresh the OAuth2 access token.

    Attempts to refresh the current OAuth2 access token using the
    refresh token stored in the client configuration. This function
    requires that the client be configured with OAuth2 authentication.

    Returns
    -------
    None

    Raises
    ------
    ClientError
        If the client is not properly configured or if the token
        refresh fails.
    """
    client: ClientDHCore = get_client(local=False)
    client._configurator.check_config()
    client._configurator.refresh_credentials()
