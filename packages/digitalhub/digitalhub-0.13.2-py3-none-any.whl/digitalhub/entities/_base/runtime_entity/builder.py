# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.utils.exceptions import EntityError


class RuntimeEntityBuilder:
    """
    RuntimeEntity builder.
    """

    EXECUTABLE_KIND: str = None
    TASKS_KINDS: dict = None
    RUN_KIND: str = None

    def __init__(self) -> None:
        if self.EXECUTABLE_KIND is None:
            raise EntityError("EXECUTABLE_KIND must be set")
        if self.TASKS_KINDS is None:
            raise EntityError("TASKS_KINDS must be set")
        if self.RUN_KIND is None:
            raise EntityError("RUN_KIND must be set")

    def get_action_from_task_kind(self, task_kind: str) -> str:
        """
        Get action from task kind.

        Parameters
        ----------
        task_kind : str
            Task kind.

        Returns
        -------
        str
            Action.
        """
        for task in self.TASKS_KINDS:
            if task["kind"] == task_kind:
                return task["action"]
        msg = f"Task kind {task_kind} not allowed."
        raise EntityError(msg)

    def get_task_kind_from_action(self, action: str) -> list[str]:
        """
        Get task kinds from action.

        Parameters
        ----------
        action : str
            Action.

        Returns
        -------
        list[str]
            Task kinds.
        """
        for task in self.TASKS_KINDS:
            if task["action"] == action:
                return task["kind"]
        msg = f"Action {action} not allowed."
        raise EntityError(msg)

    def get_run_kind(self) -> str:
        """
        Get run kind.

        Returns
        -------
        str
            Run kind.
        """
        return self.RUN_KIND

    def get_executable_kind(self) -> str:
        """
        Get executable kind.

        Returns
        -------
        str
            Executable kind.
        """
        return self.EXECUTABLE_KIND

    def get_all_kinds(self) -> list[str]:
        """
        Get all kinds.

        Returns
        -------
        list[str]
            All kinds.
        """
        task_kinds = [i["kind"] for i in self.TASKS_KINDS]
        return [self.EXECUTABLE_KIND, self.RUN_KIND, *task_kinds]

    def get_all_actions(self) -> list[str]:
        """
        Get all actions.

        Returns
        -------
        list[str]
            All actions.
        """
        return [i["action"] for i in self.TASKS_KINDS]
