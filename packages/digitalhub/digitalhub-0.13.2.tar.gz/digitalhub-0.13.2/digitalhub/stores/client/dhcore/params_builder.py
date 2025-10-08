# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities._commons.enums import ApiCategories, BackendOperations
from digitalhub.stores.client._base.params_builder import ClientParametersBuilder


class ClientDHCoreParametersBuilder(ClientParametersBuilder):
    """
    Parameter builder for DHCore client API calls.

    This class constructs HTTP request parameters for different DHCore API
    operations, handling the specific parameter formats and query structures
    required by the DigitalHub Core backend. It supports both base-level
    operations (like project management) and context-level operations
    (entity operations within projects).

    The builder handles various parameter transformations including:
    - Query parameter formatting for different operations
    - Search filter construction for Solr-based searches
    - Cascade deletion options
    - Versioning parameters
    - Entity sharing parameters

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

        Routes parameter building to the appropriate method based on the
        API category (base or context operations) and applies operation-specific
        parameter transformations.

        Parameters
        ----------
        category : str
            The API category, either 'base' for project-level operations
            or 'context' for entity operations within projects.
        operation : str
            The specific API operation being performed (create, read, update,
            delete, list, search, etc.).
        **kwargs : dict
            Raw parameters to be transformed into proper HTTP request format.
            May include entity identifiers, filter criteria, pagination
            options, etc.

        Returns
        -------
        dict
            Formatted parameters dictionary ready for HTTP request, typically
            containing a 'params' key with query parameters and other
            request-specific parameters.

        Notes
        -----
        This method acts as a dispatcher, routing to either base or context
        parameter building based on the category. All parameter dictionaries
        are initialized with a 'params' key for query parameters if not
        already present.
        """
        if category == ApiCategories.BASE.value:
            return self.build_parameters_base(operation, **kwargs)
        return self.build_parameters_context(operation, **kwargs)

    def build_parameters_base(self, operation: str, **kwargs) -> dict:
        """
        Build parameters for base-level API operations.

        Constructs HTTP request parameters for operations that work at the
        base level of the API, typically project-level operations and
        entity sharing functionality.

        Parameters
        ----------
        operation : str
            The API operation being performed. Supported operations:
            - DELETE: Project deletion with optional cascade
            - SHARE: Entity sharing/unsharing with users
        **kwargs : dict
            Operation-specific parameters including:
            - cascade (bool): For DELETE, whether to cascade delete
            - user (str): For SHARE, target user for sharing
            - unshare (bool): For SHARE, whether to unshare instead
            - id (str): For SHARE unshare, entity ID to unshare

        Returns
        -------
        dict
            Formatted parameters with 'params' containing query parameters
            and other request-specific parameters.

        Notes
        -----
        Parameter transformations:
        - CASCADE: Boolean values are converted to lowercase strings
        - SHARE: User parameter is moved to query params
        - UNSHARE: Requires both unshare=True and entity id
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

        Constructs HTTP request parameters for operations that work within
        a specific context (project), including entity management and
        search functionality.

        Parameters
        ----------
        operation : str
            The API operation being performed. Supported operations:
            - SEARCH: Search entities with filtering and pagination
            - READ_MANY: Retrieve multiple entities with pagination
            - DELETE: Delete specific entity by ID
            - READ: Read specific entity by ID (with optional embedded)
        **kwargs : dict
            Operation-specific parameters including:
            - params (dict): Search filters and conditions
            - page (int): Page number for pagination (default: 0)
            - size (int): Number of items per page (default: 20)
            - order_by (str): Field to order results by
            - order (str): Order direction ('asc' or 'desc')
            - embedded (bool): For READ, whether to include embedded entities
            - id (str): For READ/DELETE, entity identifier

        Returns
        -------
        dict
            Formatted parameters with 'params' containing query parameters
            and other request-specific parameters like 'id' for entity operations.

        Notes
        -----
        Search and pagination:
        - Filters are applied via 'filter' parameter in query string
        - Pagination uses 'page' and 'size' parameters
        - Results can be ordered using 'sort' parameter format

        Entity operations:
        - READ: Supports embedded entity inclusion via 'embedded' param
        - DELETE: Requires entity 'id' parameter
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

        Ensures that the parameter dictionary has a 'params' key for
        HTTP query parameters. This is a utility method used by all
        parameter building methods to guarantee consistent structure.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments to be formatted. May be empty or contain
            various parameters for API operations.

        Returns
        -------
        dict
            Parameters dictionary with guaranteed 'params' key containing
            an empty dict if not already present.

        Notes
        -----
        This method is called at the beginning of all parameter building
        methods to ensure consistent dictionary structure for query
        parameter handling.
        """
        if not kwargs:
            kwargs = {}
        if "params" not in kwargs:
            kwargs["params"] = {}
        return kwargs
