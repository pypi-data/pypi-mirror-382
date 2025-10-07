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
    Set DHCore environment variables and reload client configuration.

    Updates environment variables for DHCore configuration and automatically
    reloads the client configurator to apply new settings. Overwrites existing
    environment variables if already set.

    Parameters
    ----------
    endpoint : str, optional
        DHCore backend endpoint URL.
    user : str, optional
        Username for basic authentication.
    password : str, optional
        Password for basic authentication.
    access_token : str, optional
        OAuth2 access token.
    refresh_token : str, optional
        OAuth2 refresh token.
    client_id : str, optional
        OAuth2 client identifier.

    Returns
    -------
    None
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
    Refresh the current OAuth2 access token.

    Uses the refresh token stored in client configuration to obtain a new
    access token. Requires OAuth2 authentication configuration.

    Returns
    -------
    None

    Raises
    ------
    ClientError
        If client not properly configured or token refresh fails.
    """
    client: ClientDHCore = get_client(local=False)
    client._configurator.check_config()
    client._configurator.refresh_credentials()
