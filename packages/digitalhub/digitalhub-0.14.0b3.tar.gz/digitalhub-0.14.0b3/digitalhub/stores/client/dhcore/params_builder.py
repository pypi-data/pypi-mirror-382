# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities._commons.enums import ApiCategories, BackendOperations
from digitalhub.stores.client._base.params_builder import ClientParametersBuilder


class ClientDHCoreParametersBuilder(ClientParametersBuilder):
    """
    Parameter builder for DHCore client API calls.

    Constructs HTTP request parameters for DHCore API operations, handling
    parameter formats and query structures for both base-level operations
    (project management) and context-level operations (entity operations
    within projects). Supports query parameter formatting, search filter
    construction for Solr-based searches, cascade deletion options,
    versioning parameters, and entity sharing parameters.

    Methods
    -------
    build_parameters(category, operation, **kwargs)
        Main entry point for parameter building based on API category.
    build_parameters_base(operation, **kwargs)
        Builds parameters for base-level API operations.
    build_parameters_context(operation, **kwargs)
        Builds parameters for context-level API operations.
    """

    def build_parameters(self, category: str, operation: str, **kwargs) -> dict:
        """
        Build HTTP request parameters for DHCore API calls.

        Routes parameter building to appropriate method based on API category
        (base or context operations) and applies operation-specific transformations.
        Acts as dispatcher, initializing parameter dictionaries with 'params' key
        for query parameters.

        Parameters
        ----------
        category : str
            API category: 'base' for project-level operations or 'context'
            for entity operations within projects.
        operation : str
            Specific API operation (create, read, update, delete, list, search, etc.).
        **kwargs : dict
            Raw parameters to transform including entity identifiers, filter
            criteria, pagination options, etc.

        Returns
        -------
        dict
            Formatted parameters dictionary with 'params' key for query parameters
            and other request-specific parameters.
        """
        if category == ApiCategories.BASE.value:
            return self.build_parameters_base(operation, **kwargs)
        return self.build_parameters_context(operation, **kwargs)

    def build_parameters_base(self, operation: str, **kwargs) -> dict:
        """
        Build parameters for base-level API operations.

        Constructs HTTP request parameters for project-level operations and
        entity sharing functionality. Handles CASCADE (boolean to lowercase string),
        SHARE (user parameter to query params), and UNSHARE (requires unshare=True
        and entity id).

        Parameters
        ----------
        operation : str
            API operation: DELETE (project deletion with optional cascade)
            or SHARE (entity sharing/unsharing with users).
        **kwargs : dict
            Operation-specific parameters:
            - cascade (bool): For DELETE, whether to cascade delete
            - user (str): For SHARE, target user for sharing
            - unshare (bool): For SHARE, whether to unshare instead
            - id (str): For SHARE unshare, entity ID to unshare

        Returns
        -------
        dict
            Formatted parameters with 'params' containing query parameters.
        """
        kwargs = self._set_params(**kwargs)
        if operation == BackendOperations.DELETE.value:
            if (cascade := kwargs.pop("cascade", None)) is not None:
                kwargs["params"]["cascade"] = str(cascade).lower()
        elif operation == BackendOperations.SHARE.value:
            kwargs["params"]["user"] = kwargs.pop("user")
            if kwargs.pop("unshare", False):
                kwargs["params"]["id"] = kwargs.pop("id")

        return kwargs

    def build_parameters_context(self, operation: str, **kwargs) -> dict:
        """
        Build parameters for context-level API operations.

        Constructs HTTP request parameters for entity management and search within
        projects. Handles search filters via 'filter' parameter, pagination with
        'page' and 'size', result ordering with 'sort' parameter. READ supports
        embedded entity inclusion, DELETE requires entity 'id' parameter.

        Parameters
        ----------
        operation : str
            API operation: SEARCH (search entities with filtering), READ_MANY
            (retrieve multiple with pagination), DELETE (delete by ID),
            READ (read by ID with optional embedded).
        **kwargs : dict
            Operation-specific parameters:
            - params (dict): Search filters and conditions
            - page (int): Page number for pagination (default: 0)
            - size (int): Items per page (default: 20)
            - order_by (str): Field to order results by
            - order (str): Order direction ('asc' or 'desc')
            - embedded (bool): For READ, whether to include embedded entities
            - id (str): For READ/DELETE, entity identifier

        Returns
        -------
        dict
            Formatted parameters with 'params' for query parameters and
            other request-specific parameters like 'id' for entity operations.
        """
        kwargs = self._set_params(**kwargs)

        # Handle read
        if operation == BackendOperations.READ.value:
            name = kwargs.pop("entity_name", None)
            if name is not None:
                kwargs["params"]["name"] = name
        elif operation == BackendOperations.READ_ALL_VERSIONS.value:
            kwargs["params"]["versions"] = "all"
            kwargs["params"]["name"] = kwargs.pop("entity_name")
        # Handle delete
        elif operation == BackendOperations.DELETE.value:
            # Handle cascade
            if (cascade := kwargs.pop("cascade", None)) is not None:
                kwargs["params"]["cascade"] = str(cascade).lower()

            # Handle delete all versions
            entity_id = kwargs.pop("entity_id")
            entity_name = kwargs.pop("entity_name")
            if not kwargs.pop("delete_all_versions", False):
                if entity_id is None:
                    raise ValueError(
                        "If `delete_all_versions` is False, `entity_id` must be provided,"
                        " either as an argument or in key `identifier`.",
                    )
            else:
                kwargs["params"]["name"] = entity_name
        # Handle search
        elif operation == BackendOperations.SEARCH.value:
            # Handle fq
            if (fq := kwargs.pop("fq", None)) is not None:
                kwargs["params"]["fq"] = fq

            # Add search query
            if (query := kwargs.pop("query", None)) is not None:
                kwargs["params"]["q"] = query

            # Add search filters
            fq = []

            # Entity types
            if (entity_types := kwargs.pop("entity_types", None)) is not None:
                if not isinstance(entity_types, list):
                    entity_types = [entity_types]
                if len(entity_types) == 1:
                    entity_types = entity_types[0]
                else:
                    entity_types = " OR ".join(entity_types)
                fq.append(f"type:({entity_types})")

            # Name
            if (name := kwargs.pop("name", None)) is not None:
                fq.append(f'metadata.name:"{name}"')

            # Kind
            if (kind := kwargs.pop("kind", None)) is not None:
                fq.append(f'kind:"{kind}"')

            # Time
            created = kwargs.pop("created", None)
            updated = kwargs.pop("updated", None)
            created = created if created is not None else "*"
            updated = updated if updated is not None else "*"
            fq.append(f"metadata.updated:[{created} TO {updated}]")

            # Description
            if (description := kwargs.pop("description", None)) is not None:
                fq.append(f'metadata.description:"{description}"')

            # Labels
            if (labels := kwargs.pop("labels", None)) is not None:
                if len(labels) == 1:
                    labels = labels[0]
                else:
                    labels = " AND ".join(labels)
                fq.append(f"metadata.labels:({labels})")

            # Add filters
            kwargs["params"]["fq"] = fq

        return kwargs

    @staticmethod
    def _set_params(**kwargs) -> dict:
        """
        Initialize parameter dictionary with query parameters structure.

        Ensures parameter dictionary has 'params' key for HTTP query parameters,
        guaranteeing consistent structure for all parameter building methods.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments to format. May be empty or contain various
            parameters for API operations.

        Returns
        -------
        dict
            Parameters dictionary with guaranteed 'params' key containing
            empty dict if not already present.
        """
        if not kwargs:
            kwargs = {}
        if "params" not in kwargs:
            kwargs["params"] = {}
        return kwargs
