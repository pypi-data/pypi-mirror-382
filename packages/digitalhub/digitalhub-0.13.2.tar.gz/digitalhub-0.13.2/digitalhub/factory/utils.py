# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import importlib
import pkgutil
import re
from types import ModuleType

from digitalhub.factory.factory import factory


def import_module(package: str) -> ModuleType:
    """
    Import a module dynamically by package name.

    Parameters
    ----------
    package : str
        The fully qualified package name to import.

    Returns
    -------
    ModuleType
        The imported module object.

    Raises
    ------
    ModuleNotFoundError
        If the specified package cannot be found.
    RuntimeError
        If any other error occurs during import.
    """
    try:
        return importlib.import_module(package)
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(f"Package {package} not found.") from e
    except Exception as e:
        raise RuntimeError(f"An error occurred while importing {package}.") from e


def list_runtimes() -> list[str]:
    """
    List all installed DigitalHub runtime packages.

    Scans installed packages for those matching the pattern
    'digitalhub_runtime_*'.

    Returns
    -------
    list of str
        List of runtime package names.

    Raises
    ------
    RuntimeError
        If an error occurs while scanning for runtime packages.
    """
    pattern = r"digitalhub_runtime_.*"
    runtimes: list[str] = []
    try:
        for _, name, _ in pkgutil.iter_modules():
            if re.match(pattern, name):
                runtimes.append(name)
        return runtimes
    except Exception as e:
        raise RuntimeError("Error listing installed runtimes.") from e


def register_runtimes_entities() -> None:
    """
    Register all runtime builders and their entities into the factory.

    Imports each runtime package and registers its entity and runtime
    builders with the global factory instance.

    Returns
    -------
    None
    """
    for package in list_runtimes():
        module = import_module(package)
        entity_builders = getattr(module, "entity_builders")
        for entity_builder_tuple in entity_builders:
            kind, builder = entity_builder_tuple
            factory.add_entity_builder(kind, builder)

        runtime_builders = getattr(module, "runtime_builders")
        for runtime_builder_tuple in runtime_builders:
            kind, builder = runtime_builder_tuple
            factory.add_runtime_builder(kind, builder)


def register_entities() -> None:
    """
    Register core entity builders into the factory.

    Imports the core entities module and registers all entity
    builders with the global factory instance.

    Returns
    -------
    None

    Raises
    ------
    RuntimeError
        If registration of core entities fails.
    """
    try:
        module = import_module("digitalhub.entities.builders")
        entities_builders_list = getattr(module, "entity_builders")
        for entity_builder_tuple in entities_builders_list:
            kind, builder = entity_builder_tuple
            factory.add_entity_builder(kind, builder)
    except Exception as e:
        raise RuntimeError("Error registering entities.") from e
