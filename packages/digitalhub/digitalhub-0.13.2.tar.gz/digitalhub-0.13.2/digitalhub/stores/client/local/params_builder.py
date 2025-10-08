# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities._commons.enums import ApiCategories, BackendOperations
from digitalhub.stores.client._base.params_builder import ClientParametersBuilder


class ClientLocalParametersBuilder(ClientParametersBuilder):
    """
    This class is used to build the parameters for the Local client calls.
    """

    def build_parameters(self, category: str, operation: str, **kwargs) -> dict:
        """
        Build the parameters for the client call.

        Parameters
        ----------
        category : str
            API category.
        operation : str
            API operation.
        **kwargs : dict
            Parameters to build.

        Returns
        -------
        dict
            Parameters formatted.
        """
        if category == ApiCategories.BASE.value:
            return self.build_parameters_base(operation, **kwargs)
        return self.build_parameters_context(operation, **kwargs)

    def build_parameters_base(self, operation: str, **kwargs) -> dict:
        """
        Build the base parameters for the client call.

        Parameters
        ----------
        operation : str
            API operation.
        **kwargs : dict
            Parameters to build.

        Returns
        -------
        dict
            Parameters formatted.
        """
        kwargs = self._set_params(**kwargs)
        if operation == BackendOperations.DELETE.value:
            if (cascade := kwargs.pop("cascade", None)) is not None:
                kwargs["params"]["cascade"] = str(cascade).lower()
        return kwargs

    def build_parameters_context(self, operation: str, **kwargs) -> dict:
        """
        Build the context parameters for the client call.

        Parameters
        ----------
        operation : str
            API operation.
        **kwargs : dict
            Parameters to build.

        Returns
        -------
        dict
            Parameters formatted.
        """
        kwargs = self._set_params(**kwargs)

        # Handle read
        if operation == BackendOperations.READ_ALL_VERSIONS.value:
            kwargs["params"]["versions"] = "all"
            kwargs["params"]["name"] = kwargs.pop("entity_name")
        # Handle delete
        elif operation == BackendOperations.DELETE.value:
            # Handle cascade
            if cascade := kwargs.pop("cascade", None) is not None:
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
        return kwargs

    @staticmethod
    def _set_params(**kwargs) -> dict:
        """
        Format params parameter.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments.

        Returns
        -------
        dict
            Parameters with initialized params.
        """
        if not kwargs:
            kwargs = {}
        if "params" not in kwargs:
            kwargs["params"] = {}
        return kwargs
