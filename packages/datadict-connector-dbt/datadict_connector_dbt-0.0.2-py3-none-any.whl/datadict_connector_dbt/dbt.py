"""
The DBT connector for DataDict.
"""

from datadict_connector_base import (
    CatalogLoaderV2,
    ChangeApplier,
    ConnectorBase,
    MetadataSource,
    PathBuilder,
)

from .dbt_applier import DbtApplier
from .dbt_loader import DbtLoader
from .dbt_path_builder import DbtPathBuilder
from .dbt_source import DbtManifestSource


class DbtConnector(ConnectorBase):
    """
    DBT connector implementation.
    Provides factory methods for creating loader, applier, and path builder instances.

    Note: DBT does not currently have a metadata source implementation as DBT
    catalogs are typically filesystem-based rather than pulled from a remote source.
    """

    def make_loader(self) -> CatalogLoaderV2:
        """
        Create a DBT catalog loader.

        Returns:
            DbtLoader instance
        """
        return DbtLoader()

    def make_path_builder(self, lookup_table: dict[str, str]) -> PathBuilder:
        """
        Create a DBT path builder.

        Args:
            lookup_table: Dict mapping FQN keys to existing file paths

        Returns:
            DbtPathBuilder instance
        """
        return DbtPathBuilder(lookup_table)

    def make_applier(self) -> ChangeApplier:
        """
        Create a DBT change applier.

        Returns:
            DbtApplier instance
        """
        return DbtApplier()

    def make_source(self) -> MetadataSource:
        """
        Create a DBT metadata source.

        Returns a source that can parse DBT's manifest.json file to extract
        metadata about models, seeds, exposures, and their columns.

        Returns:
            DbtManifestSource instance
        """
        return DbtManifestSource()
