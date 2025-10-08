# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing

from digitalhub.stores.client.builder import client_builder

if typing.TYPE_CHECKING:
    from digitalhub.stores.client._base.client import Client


def get_client(local: bool = False, config: dict | None = None) -> Client:
    """
    Wrapper around ClientBuilder.build.

    Parameters
    ----------
    local : bool, default False
        Whether to create a local client or not. If True, creates a
        ClientLocal instance that operates in-memory. If False, creates
        a ClientDHCore instance that communicates with a remote backend.
    config : dict, optional
        DHCore environment configuration. Only used when local=False.
        If None, configuration will be loaded from environment variables
        and configuration files.

    Returns
    -------
    Client
        The client instance. Either ClientLocal or ClientDHCore depending
        on the local parameter.
    """
    return client_builder.build(local, config)
