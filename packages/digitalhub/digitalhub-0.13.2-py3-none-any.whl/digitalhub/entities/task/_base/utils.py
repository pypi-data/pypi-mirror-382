# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations


def build_task_actions(kind_action_list: list[tuple[str, str]]) -> list[dict[str, str]]:
    """
    Build task actions.

    Parameters
    ----------
    kind_action_list : list[tuple[str, str]]
        List of kind-action couples.

    Returns
    -------
    list[dict[str, str]]
        Returns the task actions.
    """
    return [{"kind": kind, "action": action} for (kind, action) in kind_action_list]
