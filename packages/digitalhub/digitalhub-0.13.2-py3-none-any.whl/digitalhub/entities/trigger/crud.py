# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing

from digitalhub.entities._commons.enums import EntityTypes
from digitalhub.entities._processors.context import context_processor

if typing.TYPE_CHECKING:
    from digitalhub.entities.trigger._base.entity import Trigger


ENTITY_TYPE = EntityTypes.TRIGGER.value


def new_trigger(
    project: str,
    name: str,
    kind: str,
    task: str,
    function: str | None = None,
    workflow: str | None = None,
    uuid: str | None = None,
    description: str | None = None,
    labels: list[str] | None = None,
    embedded: bool = False,
    template: dict | None = None,
    **kwargs,
) -> Trigger:
    """
    Create a new object.

    Parameters
    ----------
    project : str
        Project name.
    name : str
        Object name.
    kind : str
        Kind the object.
    uuid : str
        ID of the object.
    description : str
        Description of the object (human readable).
    labels : list[str]
        List of labels.
    embedded : bool
        Flag to determine if object spec must be embedded in project spec.
    **kwargs : dict
        Spec keyword arguments.

    Returns
    -------
    Trigger
        Object instance.

    Examples
    --------
    >>> obj = new_trigger(project="my-project",
    >>>                   kind="trigger",
    >>>                   name="my-trigger",)
    """
    if workflow is None and function is None:
        raise ValueError("Workflow or function must be provided")
    if kwargs is None:
        kwargs = {}
    if template is None:
        template = {}
    template["task"] = task
    if workflow is not None:
        template["workflow"] = workflow
    if function is not None:
        template["function"] = function
    kwargs["template"] = template
    return context_processor.create_context_entity(
        project=project,
        name=name,
        kind=kind,
        uuid=uuid,
        description=description,
        labels=labels,
        embedded=embedded,
        **kwargs,
    )


def get_trigger(
    identifier: str,
    project: str | None = None,
    entity_id: str | None = None,
    **kwargs,
) -> Trigger:
    """
    Get object from backend.

    Parameters
    ----------
    identifier : str
        Entity key (store://...) or entity name.
    project : str
        Project name.
    entity_id : str
        Entity ID.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    Trigger
        Object instance.

    Examples
    --------
    Using entity key:
    >>> obj = get_trigger("store://my-trigger-key")

    Using entity name:
    >>> obj = get_trigger("my-trigger-name"
    >>>                  project="my-project",
    >>>                  entity_id="my-trigger-id")
    """
    return context_processor.read_context_entity(
        identifier,
        entity_type=ENTITY_TYPE,
        project=project,
        entity_id=entity_id,
        **kwargs,
    )


def get_trigger_versions(
    identifier: str,
    project: str | None = None,
    **kwargs,
) -> list[Trigger]:
    """
    Get object versions from backend.

    Parameters
    ----------
    identifier : str
        Entity key (store://...) or entity name.
    project : str
        Project name.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    list[Trigger]
        List of object instances.

    Examples
    --------
    Using entity key:
    >>> objs = get_trigger_versions("store://my-trigger-key")

    Using entity name:
    >>> objs = get_trigger_versions("my-trigger-name",
    >>>                            project="my-project")
    """
    return context_processor.read_context_entity_versions(
        identifier,
        entity_type=ENTITY_TYPE,
        project=project,
        **kwargs,
    )


def list_triggers(project: str, **kwargs) -> list[Trigger]:
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
    list[Trigger]
        List of object instances.

    Examples
    --------
    >>> objs = list_triggers(project="my-project")
    """
    return context_processor.list_context_entities(
        project=project,
        entity_type=ENTITY_TYPE,
        **kwargs,
    )


def import_trigger(file: str) -> Trigger:
    """
    Import object from a YAML file and create a new object into the backend.

    Parameters
    ----------
    file : str
        Path to YAML file.

    Returns
    -------
    Trigger
        Object instance.

    Examples
    --------
    >>> obj = import_trigger("my-trigger.yaml")
    """
    return context_processor.import_context_entity(file)


def load_trigger(file: str) -> Trigger:
    """
    Load object from a YAML file and update an existing object into the backend.

    Parameters
    ----------
    file : str
        Path to YAML file.

    Returns
    -------
    Trigger
        Object instance.

    Examples
    --------
    >>> obj = load_trigger("my-trigger.yaml")
    """
    return context_processor.load_context_entity(file)


def update_trigger(entity: Trigger) -> Trigger:
    """
    Update object. Note that object spec are immutable.

    Parameters
    ----------
    entity : Trigger
        Object to update.

    Returns
    -------
    Trigger
        Entity updated.

    Examples
    --------
    >>> obj = update_trigger(obj)
    """
    return context_processor.update_context_entity(
        project=entity.project,
        entity_type=entity.ENTITY_TYPE,
        entity_id=entity.id,
        entity_dict=entity.to_dict(),
    )


def delete_trigger(
    identifier: str,
    project: str | None = None,
    entity_id: str | None = None,
    delete_all_versions: bool = False,
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
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    dict
        Response from backend.

    Examples
    --------
    If delete_all_versions is False:
    >>> obj = delete_trigger("store://my-trigger-key")

    Otherwise:
    >>> obj = delete_trigger("my-trigger-name"
    >>>                     project="my-project",
    >>>                     delete_all_versions=True)
    """
    return context_processor.delete_context_entity(
        identifier=identifier,
        entity_type=ENTITY_TYPE,
        project=project,
        entity_id=entity_id,
        delete_all_versions=delete_all_versions,
        **kwargs,
    )
