# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pydantic import BaseModel


class ClientConfig(BaseModel):
    """Client configuration model."""

    endpoint: str
    """API endpoint."""


class BasicAuth(ClientConfig):
    """Basic authentication model."""

    user: str
    """Username."""

    password: str
    """Basic authentication password."""


class OAuth2TokenAuth(ClientConfig):
    """OAuth2 token authentication model."""

    access_token: str
    """OAuth2 token."""

    refresh_token: str
    """OAuth2 refresh token."""

    client_id: str
    """OAuth2 client id."""

    issuer_endpoint: str
    """OAuth2 issuer endpoint."""
