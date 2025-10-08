# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing

from digitalhub.entities._commons.enums import EntityTypes
from digitalhub.entities._processors.context import context_processor
from digitalhub.utils.exceptions import EntityError

if typing.TYPE_CHECKING:
    from digitalhub.entities.task._base.entity import Task


ENTITY_TYPE = EntityTypes.TASK.value


def new_task(
    project: str,
    kind: str,
    uuid: str | None = None,
    labels: list[str] | None = None,
    function: str | None = None,
    workflow: str | None = None,
    **kwargs,
) -> Task:
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
    function : str
        Name of the executable associated with the task.
    workflow : str
        Name of the workflow associated with the task.
    **kwargs : dict
        Spec keyword arguments.

    Returns
    -------
    Task
        Object instance.

    Examples
    --------
    >>> obj = new_task(project="my-project",
    >>>                kind="python+job",
    >>>                function="function-string")
    """
    return context_processor.create_context_entity(
        project=project,
        kind=kind,
        uuid=uuid,
        labels=labels,
        function=function,
        workflow=workflow,
        **kwargs,
    )


def get_task(
    identifier: str,
    project: str | None = None,
    **kwargs,
) -> Task:
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
    Task
        Object instance.

    Examples
    --------
    Using entity key:
    >>> obj = get_task("store://my-task-key")

    Using entity ID:
    >>> obj = get_task("my-task-id"
    >>>               project="my-project")
    """
    return context_processor.read_unversioned_entity(
        identifier,
        entity_type=ENTITY_TYPE,
        project=project,
        **kwargs,
    )


def list_tasks(project: str, **kwargs) -> list[Task]:
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
    list[Task]
        List of object instances.

    Examples
    --------
    >>> objs = list_tasks(project="my-project")
    """
    return context_processor.list_context_entities(
        project=project,
        entity_type=ENTITY_TYPE,
        **kwargs,
    )


def import_task(file: str) -> Task:
    """
    Import object from a YAML file and create a new object into the backend.

    Parameters
    ----------
    file : str
        Path to YAML file.

    Returns
    -------
    Task
        Object instance.

    Example
    -------
    >>> obj = import_task("my-task.yaml")
    """
    return context_processor.import_context_entity(file)


def load_task(file: str) -> Task:
    """
    Load object from a YAML file and update an existing object into the backend.

    Parameters
    ----------
    file : str
        Path to YAML file.

    Returns
    -------
    Task
        Object instance.

    Examples
    --------
    >>> obj = load_task("my-task.yaml")
    """
    return context_processor.load_context_entity(file)


def update_task(entity: Task) -> Task:
    """
    Update object. Note that object spec are immutable.

    Parameters
    ----------
    entity : Task
        Object to update.

    Returns
    -------
    Task
        Entity updated.

    Examples
    --------
    >>> obj = update_task(obj)
    """
    return context_processor.update_context_entity(
        project=entity.project,
        entity_type=entity.ENTITY_TYPE,
        entity_id=entity.id,
        entity_dict=entity.to_dict(),
    )


def delete_task(
    identifier: str,
    project: str | None = None,
    entity_id: str | None = None,
    delete_all_versions: bool = False,
    cascade: bool = True,
    **kwargs,
) -> dict:
    """
    Delete object from backend.

    Parameters
    ----------
    identifier : str
        Entity key (store://...) or entity name.
    project : str
        Project name.
    entity_id : str
        Entity ID.
    delete_all_versions : bool
        Delete all versions of the named entity. If True, use entity name instead of entity key as identifier.
    cascade : bool
        Cascade delete.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    dict
        Response from backend.

    Examples
    --------
    If delete_all_versions is False:
    >>> obj = delete_task("store://my-task-key")

    Otherwise:
    >>> obj = delete_task("task-name",
    >>>                  project="my-project",
    >>>                  delete_all_versions=True)
    """
    if not identifier.startswith("store://"):
        raise EntityError("Task has no name. Use key instead.")
    return context_processor.delete_context_entity(
        identifier=identifier,
        entity_type=ENTITY_TYPE,
        project=project,
        entity_id=entity_id,
        delete_all_versions=delete_all_versions,
        cascade=cascade,
        **kwargs,
    )
