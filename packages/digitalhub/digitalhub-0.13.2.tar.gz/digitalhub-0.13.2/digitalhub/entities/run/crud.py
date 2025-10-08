# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing

from digitalhub.entities._commons.enums import EntityTypes
from digitalhub.entities._processors.context import context_processor
from digitalhub.utils.exceptions import EntityError

if typing.TYPE_CHECKING:
    from digitalhub.entities.run._base.entity import Run


ENTITY_TYPE = EntityTypes.RUN.value


def new_run(
    project: str,
    kind: str,
    uuid: str | None = None,
    labels: list[str] | None = None,
    task: str | None = None,
    local_execution: bool = False,
    **kwargs,
) -> Run:
    """
    Create a new object.

    Parameters
    ----------
    project : str
        Project name.
    kind : str
        Kind the object.
    uuid : str
        ID of the object.
    labels : list[str]
        List of labels.
    task : str
        Name of the task associated with the run.
    local_execution : bool
        Flag to determine if object has local execution.
    **kwargs : dict
        Spec keyword arguments.

    Returns
    -------
    Run
        Object instance.

    Examples
    --------
    >>> obj = new_run(project="my-project",
    >>>               kind="python+run",
    >>>               task="task-string")
    """
    return context_processor.create_context_entity(
        project=project,
        kind=kind,
        uuid=uuid,
        labels=labels,
        task=task,
        local_execution=local_execution,
        **kwargs,
    )


def get_run(
    identifier: str,
    project: str | None = None,
    **kwargs,
) -> Run:
    """
    Get object from backend.

    Parameters
    ----------
    identifier : str
        Entity key (store://...) or entity ID.
    project : str
        Project name.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    Run
        Object instance.

    Examples
    --------
    Using entity key:
    >>> obj = get_run("store://my-run-key")

    Using entity ID:
    >>> obj = get_run("my-run-id"
    >>>               project="my-project")
    """
    return context_processor.read_unversioned_entity(
        identifier,
        entity_type=ENTITY_TYPE,
        project=project,
        **kwargs,
    )


def list_runs(project: str, **kwargs) -> list[Run]:
    """
    List all latest version objects from backend.

    Parameters
    ----------
    project : str
        Project name.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    list[Run]
        List of object instances.

    Examples
    --------
    >>> objs = list_runs(project="my-project")
    """
    # TODO more examples: search by function, latest for task and function
    return context_processor.list_context_entities(
        project=project,
        entity_type=ENTITY_TYPE,
        **kwargs,
    )


def import_run(file: str) -> Run:
    """
    Import object from a YAML file and create a new object into the backend.

    Parameters
    ----------
    file : str
        Path to YAML file.

    Returns
    -------
    Run
        Object instance.

    Example
    -------
    >>> obj = import_run("my-run.yaml")
    """
    return context_processor.import_context_entity(file)


def load_run(file: str) -> Run:
    """
    Load object from a YAML file and update an existing object into the backend.

    Parameters
    ----------
    file : str
        Path to YAML file.

    Returns
    -------
    Run
        Object instance.

    Examples
    --------
    >>> obj = load_run("my-run.yaml")
    """
    return context_processor.load_context_entity(file)


def update_run(entity: Run) -> Run:
    """
    Update object. Note that object spec are immutable.

    Parameters
    ----------
    entity : Run
        Object to update.

    Returns
    -------
    Run
        Entity updated.

    Examples
    --------
    >>> obj = update_run(obj)
    """
    return context_processor.update_context_entity(
        project=entity.project,
        entity_type=entity.ENTITY_TYPE,
        entity_id=entity.id,
        entity_dict=entity.to_dict(),
    )


def delete_run(
    identifier: str,
    project: str | None = None,
    **kwargs,
) -> dict:
    """
    Delete object from backend.

    Parameters
    ----------
    identifier : str
        Entity key (store://...) or entity ID.
    project : str
        Project name.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    dict
        Response from backend.

    Examples
    --------
    >>> obj = delete_run("store://my-run-key")
    >>> obj = delete_run("my-run-id", project="my-project")
    """
    if not identifier.startswith("store://") and project is None:
        raise EntityError("Specify entity key or entity ID combined with project")
    return context_processor.delete_context_entity(
        identifier=identifier,
        entity_type=ENTITY_TYPE,
        project=project,
        entity_id=identifier,
        **kwargs,
    )
