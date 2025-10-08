# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing

from digitalhub.utils.exceptions import BuilderError

if typing.TYPE_CHECKING:
    from digitalhub.entities._base.entity.builder import EntityBuilder
    from digitalhub.entities._base.entity.entity import Entity
    from digitalhub.entities._base.entity.metadata import Metadata
    from digitalhub.entities._base.entity.spec import Spec, SpecValidator
    from digitalhub.entities._base.entity.status import Status
    from digitalhub.entities._base.runtime_entity.builder import RuntimeEntityBuilder
    from digitalhub.runtimes._base import Runtime
    from digitalhub.runtimes.builder import RuntimeBuilder


class Factory:
    """
    Factory for creating and managing entity and runtime builders.

    This class implements the Factory pattern to manage the creation of
    entities and runtimes through their respective builders. It maintains
    separate registries for entity and runtime builders.

    Many function arguments are called kind_to_build_from to avoid overwriting
    kind in kwargs.

    Attributes
    ----------
    _entity_builders : dict[str, EntityBuilder | RuntimeEntityBuilder]
        Registry of entity builders indexed by kind.
    _runtime_builders : dict[str, RuntimeBuilder]
        Registry of runtime builders indexed by kind.

    Notes
    -----
    All builder methods may raise BuilderError if the requested kind
    is not found in the registry.
    """

    def __init__(self):
        self._entity_builders: dict[str, EntityBuilder | RuntimeEntityBuilder] = {}
        self._runtime_builders: dict[str, RuntimeBuilder] = {}

    def add_entity_builder(self, name: str, builder: EntityBuilder | RuntimeEntityBuilder) -> None:
        """
        Register an entity builder.

        Parameters
        ----------
        name : str
            The unique identifier for the builder.
        builder : EntityBuilder or RuntimeEntityBuilder
            The builder instance to register.

        Returns
        -------
        None

        Raises
        ------
        BuilderError
            If a builder with the same name already exists.
        """
        if name in self._entity_builders:
            raise BuilderError(f"Builder {name} already exists.")
        self._entity_builders[name] = builder()

    def add_runtime_builder(self, name: str, builder: RuntimeBuilder) -> None:
        """
        Register a runtime builder.

        Parameters
        ----------
        name : str
            The unique identifier for the builder.
        builder : RuntimeBuilder
            The builder instance to register.

        Returns
        -------
        None

        Raises
        ------
        BuilderError
            If a builder with the same name already exists.
        """
        if name in self._runtime_builders:
            raise BuilderError(f"Builder {name} already exists.")
        self._runtime_builders[name] = builder()

    def build_entity_from_params(self, **kwargs) -> Entity:
        """
        Build an entity from parameters.

        Parameters
        ----------
        **kwargs
            Entity parameters.

        Returns
        -------
        Entity
            Entity object.
        """
        try:
            kind = kwargs["kind"]
        except KeyError:
            raise BuilderError("Missing 'kind' parameter.")
        self._raise_if_entity_builder_not_found(kind)
        return self._entity_builders[kind].build(**kwargs)

    def build_entity_from_dict(self, obj: dict) -> Entity:
        """
        Build an entity from a dictionary.

        Parameters
        ----------
        obj : dict
            Dictionary with entity data.

        Returns
        -------
        Entity
            Entity object.
        """
        try:
            kind = obj["kind"]
        except KeyError:
            raise BuilderError("Missing 'kind' parameter.")
        self._raise_if_entity_builder_not_found(kind)
        return self._entity_builders[kind].from_dict(obj)

    def build_spec(self, kind_to_build_from: str, **kwargs) -> Spec:
        """
        Build an entity spec.

        Parameters
        ----------
        kind_to_build_from : str
            Entity type.
        **kwargs
            Additional spec parameters.

        Returns
        -------
        Spec
            Spec object.
        """
        self._raise_if_entity_builder_not_found(kind_to_build_from)
        return self._entity_builders[kind_to_build_from].build_spec(**kwargs)

    def build_metadata(self, kind_to_build_from: str, **kwargs) -> Metadata:
        """
        Build an entity metadata.

        Parameters
        ----------
        kind_to_build_from : str
            Entity type.
        **kwargs
            Additional metadata parameters.

        Returns
        -------
        Metadata
            Metadata object.
        """
        self._raise_if_entity_builder_not_found(kind_to_build_from)
        return self._entity_builders[kind_to_build_from].build_metadata(**kwargs)

    def build_status(self, kind_to_build_from: str, **kwargs) -> Status:
        """
        Build an entity status.

        Parameters
        ----------
        kind_to_build_from : str
            Entity type.
        **kwargs
            Additional status parameters.

        Returns
        -------
        Status
            Status object.
        """
        self._raise_if_entity_builder_not_found(kind_to_build_from)
        return self._entity_builders[kind_to_build_from].build_status(**kwargs)

    def build_runtime(self, kind_to_build_from: str, project: str) -> Runtime:
        """
        Build a runtime.

        Parameters
        ----------
        kind_to_build_from : str
            Runtime type.
        project : str
            Project name.

        Returns
        -------
        Runtime
            Runtime object.
        """
        self._raise_if_runtime_builder_not_found(kind_to_build_from)
        return self._runtime_builders[kind_to_build_from].build(project=project)

    def get_entity_type_from_kind(self, kind: str) -> str:
        """
        Get entity type from builder.

        Parameters
        ----------
        kind : str
            Entity type.

        Returns
        -------
        str
            Entity type.
        """
        self._raise_if_entity_builder_not_found(kind)
        return self._entity_builders[kind].get_entity_type()

    def get_executable_kind(self, kind: str) -> str:
        """
        Get executable kind.

        Parameters
        ----------
        kind : str
            Kind.

        Returns
        -------
        str
            Executable kind.
        """
        self._raise_if_entity_builder_not_found(kind)
        return self._entity_builders[kind].get_executable_kind()

    def get_action_from_task_kind(self, kind: str, task_kind: str) -> str:
        """
        Get action from task.

        Parameters
        ----------
        kind : str
            Kind.
        task_kind : str
            Task kind.

        Returns
        -------
        str
            Action.
        """
        self._raise_if_entity_builder_not_found(kind)
        return self._entity_builders[kind].get_action_from_task_kind(task_kind)

    def get_task_kind_from_action(self, kind: str, action: str) -> list[str]:
        """
        Get task kinds from action.

        Parameters
        ----------
        kind : str
            Kind.
        action : str
            Action.

        Returns
        -------
        list of str
            Task kinds.
        """
        self._raise_if_entity_builder_not_found(kind)
        return self._entity_builders[kind].get_task_kind_from_action(action)

    def get_run_kind(self, kind: str) -> str:
        """
        Get run kind.

        Parameters
        ----------
        kind : str
            Kind.

        Returns
        -------
        str
            Run kind.
        """
        self._raise_if_entity_builder_not_found(kind)
        return self._entity_builders[kind].get_run_kind()

    def get_all_kinds(self, kind: str) -> list[str]:
        """
        Get all kinds.

        Parameters
        ----------
        kind : str
            Kind.

        Returns
        -------
        list of str
            All kinds.
        """
        return self._entity_builders[kind].get_all_kinds()

    def get_spec_validator(self, kind: str) -> SpecValidator:
        """
        Get spec validators.

        Parameters
        ----------
        kind : str
            Kind.

        Returns
        -------
        SpecValidator
            Spec validator.
        """
        self._raise_if_entity_builder_not_found(kind)
        return self._entity_builders[kind].get_spec_validator()

    def _raise_if_entity_builder_not_found(self, kind: str) -> None:
        """
        Verify entity builder existence.

        Parameters
        ----------
        kind : str
            The entity kind to verify.

        Returns
        -------
        None

        Raises
        ------
        BuilderError
            If no builder exists for the specified kind.
        """
        if kind not in self._entity_builders:
            raise BuilderError(f"Entity builder for kind '{kind}' not found.")

    def _raise_if_runtime_builder_not_found(self, kind: str) -> None:
        """
        Verify runtime builder existence.

        Parameters
        ----------
        kind : str
            The runtime kind to verify.

        Returns
        -------
        None

        Raises
        ------
        BuilderError
            If no builder exists for the specified kind.
        """
        if kind not in self._runtime_builders:
            raise BuilderError(f"Runtime builder for kind '{kind}' not found.")


factory = Factory()
