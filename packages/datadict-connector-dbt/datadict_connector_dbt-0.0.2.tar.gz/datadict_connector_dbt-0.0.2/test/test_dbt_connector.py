"""
Tests for DBT connector factory.
"""

from datadict_connector_base import CatalogLoaderV2, ChangeApplier, MetadataSource, PathBuilder
from datadict_connector_dbt import (
    DbtApplier,
    DbtConnector,
    DbtLoader,
    DbtManifestSource,
    DbtPathBuilder,
)


class TestDbtConnector:
    """Test DBT connector factory methods."""

    def test_create_connector(self):
        """Test creating a connector instance."""
        connector = DbtConnector()
        assert connector is not None

    def test_make_loader(self):
        """Test make_loader factory method."""
        connector = DbtConnector()
        loader = connector.make_loader()

        assert loader is not None
        assert isinstance(loader, CatalogLoaderV2)
        assert isinstance(loader, DbtLoader)

    def test_make_path_builder(self):
        """Test make_path_builder factory method."""
        connector = DbtConnector()
        lookup_table = {"model.my_project.test": "test/path.yml"}
        path_builder = connector.make_path_builder(lookup_table)

        assert path_builder is not None
        assert isinstance(path_builder, PathBuilder)
        assert isinstance(path_builder, DbtPathBuilder)

    def test_make_path_builder_with_empty_lookup(self):
        """Test make_path_builder with empty lookup table."""
        connector = DbtConnector()
        path_builder = connector.make_path_builder({})

        assert path_builder is not None
        assert isinstance(path_builder, DbtPathBuilder)

    def test_make_applier(self):
        """Test make_applier factory method."""
        connector = DbtConnector()
        applier = connector.make_applier()

        assert applier is not None
        assert isinstance(applier, ChangeApplier)
        assert isinstance(applier, DbtApplier)

    def test_make_source(self):
        """Test make_source factory method."""
        connector = DbtConnector()
        source = connector.make_source()

        assert source is not None
        assert isinstance(source, MetadataSource)
        assert isinstance(source, DbtManifestSource)

    def test_all_components_independent(self):
        """Test that all components can be created independently."""
        connector = DbtConnector()

        loader = connector.make_loader()
        path_builder = connector.make_path_builder({})
        applier = connector.make_applier()
        source = connector.make_source()

        # All should be independent instances
        assert loader is not None
        assert path_builder is not None
        assert applier is not None
        assert source is not None

    def test_multiple_instances(self):
        """Test creating multiple instances of the same component."""
        connector = DbtConnector()

        loader1 = connector.make_loader()
        loader2 = connector.make_loader()

        # Should create new instances each time
        assert loader1 is not loader2

    def test_connector_is_stateless(self):
        """Test that connector doesn't maintain state."""
        connector = DbtConnector()

        # Creating components shouldn't affect connector state
        connector.make_loader()
        connector.make_path_builder({})
        connector.make_applier()
        connector.make_source()

        # Should still be able to create more
        loader = connector.make_loader()
        assert loader is not None

    def test_connector_can_be_cached(self):
        """Test that connector instance can be reused (long-lived)."""
        connector = DbtConnector()

        # Create multiple components from same connector
        loader1 = connector.make_loader()
        loader2 = connector.make_loader()
        source1 = connector.make_source()
        source2 = connector.make_source()

        # All should work independently
        assert loader1 is not None
        assert loader2 is not None
        assert source1 is not None
        assert source2 is not None

    def test_path_builder_receives_lookup_table(self):
        """Test that path builder is initialized with lookup table."""
        connector = DbtConnector()
        lookup_table = {
            "model.my_project.customers": "custom/customers.yml",
            "model.my_project.orders": "custom/orders.yml",
        }

        path_builder = connector.make_path_builder(lookup_table)

        # Path builder should use the lookup table
        assert path_builder is not None
        # The lookup table is passed to the constructor
        assert hasattr(path_builder, "lookup_table")
