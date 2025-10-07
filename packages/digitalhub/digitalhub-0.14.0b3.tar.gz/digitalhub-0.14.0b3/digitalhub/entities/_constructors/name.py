# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pydantic import BaseModel, Field

NAME_REGEX = r"^[a-zA-Z0-9._+-]+$"


class NameValidator(BaseModel):
    """
    Validate name format.
    """

    name: str = Field(min_length=1, max_length=256, pattern=NAME_REGEX)


def build_name(name: str) -> str:
    """
    Build name.

    Parameters
    ----------
    name : str
        The name.

    Returns
    -------
    str
        The name.
    """
    NameValidator(name=name)
    return name
