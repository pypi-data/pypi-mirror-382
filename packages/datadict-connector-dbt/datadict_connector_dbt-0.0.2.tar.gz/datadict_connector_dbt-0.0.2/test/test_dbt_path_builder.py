"""
Tests for DBT path builder.
"""

import pytest
from datadict_connector_base import ItemType
from datadict_connector_dbt import DbtPathBuilder


class TestDbtPathBuilder:
    """Test DBT path builder functionality."""

    def test_create_path_builder(self):
        """Test creating a path builder instance."""
        path_builder = DbtPathBuilder({})
        assert path_builder is not None

    def test_model_path(self):
        """Test path generation for model."""
        path_builder = DbtPathBuilder({})
        path = path_builder.get_path("model.my_project.customers", ItemType.TABLE)
        assert path == "models/customers.yml"

    def test_exposure_path(self):
        """Test path generation for exposure."""
        path_builder = DbtPathBuilder({})
        path = path_builder.get_path("exposure.my_project.sales_dashboard", ItemType.DOC)
        assert path == "exposures/sales_dashboard.yml"

    def test_seed_path(self):
        """Test path generation for seed."""
        path_builder = DbtPathBuilder({})
        path = path_builder.get_path("seed.my_project.countries", ItemType.TABLE)
        assert path == "seed/countries.yml"

    def test_column_path_matches_parent(self):
        """Test that column path matches parent model path."""
        path_builder = DbtPathBuilder({})
        model_path = path_builder.get_path("model.my_project.customers", ItemType.TABLE)
        column_path = path_builder.get_path(
            "model.my_project.customers.customer_id", ItemType.COLUMN
        )
        assert column_path == model_path

    def test_seed_column_path_matches_parent(self):
        """Test that seed column path matches parent seed path."""
        path_builder = DbtPathBuilder({})
        seed_path = path_builder.get_path("seed.my_project.countries", ItemType.TABLE)
        column_path = path_builder.get_path(
            "seed.my_project.countries.country_code", ItemType.COLUMN
        )
        assert column_path == seed_path

    def test_lookup_table_fallback(self):
        """Test fallback to default when not in lookup table."""
        lookup_table = {
            "model.my_project.orders": "custom/orders.yml",
        }
        path_builder = DbtPathBuilder(lookup_table)

        # Not in lookup table, should use default
        path = path_builder.get_path("model.my_project.customers", ItemType.TABLE)
        assert path == "models/customers.yml"

    def test_different_package_names(self):
        """Test paths for models in different packages."""
        path_builder = DbtPathBuilder({})

        path1 = path_builder.get_path("model.project1.customers", ItemType.TABLE)
        path2 = path_builder.get_path("model.project2.customers", ItemType.TABLE)

        # Same filename since only object name is used
        assert path1 == "models/customers.yml"
        assert path2 == "models/customers.yml"

    def test_special_characters_in_names(self):
        """Test handling of special characters in object names."""
        path_builder = DbtPathBuilder({})

        # Should be slugified
        path = path_builder.get_path("model.my_project.my_special_model", ItemType.TABLE)
        assert path == "models/my_special_model.yml"

    def test_invalid_dbt_key_raises_error(self):
        """Test error handling for invalid DBT keys."""
        path_builder = DbtPathBuilder({})

        with pytest.raises(ValueError, match="Invalid DBT key"):
            path_builder.get_path("invalid.key", ItemType.TABLE)

    def test_get_default_path_method(self):
        """Test get_default_path method directly."""
        path_builder = DbtPathBuilder({})

        # Model
        path = path_builder.get_default_path("model.my_project.customers", ItemType.TABLE)
        assert path == "models/customers.yml"

        # Exposure
        path = path_builder.get_default_path("exposure.my_project.dashboard", ItemType.DOC)
        assert path == "exposures/dashboard.yml"

        # Seed
        path = path_builder.get_default_path("seed.my_project.countries", ItemType.TABLE)
        assert path == "seed/countries.yml"

    def test_long_model_names(self):
        """Test handling of very long model names."""
        path_builder = DbtPathBuilder({})

        long_name = "a" * 100
        path = path_builder.get_path(f"model.my_project.{long_name}", ItemType.TABLE)

        # Should be slugified and possibly truncated
        assert path.startswith("models/")
        assert path.endswith(".yml")

    def test_model_with_version(self):
        """Test handling model names that might have version info."""
        path_builder = DbtPathBuilder({})

        path = path_builder.get_path("model.my_project.customers_v2", ItemType.TABLE)
        assert path == "models/customers_v2.yml"

    def test_three_part_key_minimum(self):
        """Test that keys must have at least 3 parts (resource.package.name)."""
        path_builder = DbtPathBuilder({})

        # Two-part key should fail
        with pytest.raises(ValueError):
            path_builder.get_path("model.my_project", ItemType.TABLE)

    def test_unsupported_resource_type(self):
        """Test error for unsupported resource types."""
        path_builder = DbtPathBuilder({})

        with pytest.raises(ValueError, match="Unsupported resource type"):
            path_builder.get_path("test.my_project.some_test", ItemType.TABLE)

    def test_slugify_removes_unsafe_chars(self):
        """Test that slugify removes filesystem-unsafe characters."""
        path_builder = DbtPathBuilder({})

        # Model name with spaces and special chars
        path = path_builder.get_path("model.my_project.My Model!", ItemType.TABLE)

        # Should not contain unsafe characters
        assert " " not in path
        assert "!" not in path
        assert path == "models/my_model.yml"

    def test_multiple_columns_same_file(self):
        """Test that multiple columns from same model use same path."""
        path_builder = DbtPathBuilder({})

        col1_path = path_builder.get_path("model.my_project.customers.id", ItemType.COLUMN)
        col2_path = path_builder.get_path("model.my_project.customers.email", ItemType.COLUMN)

        assert col1_path == col2_path
        assert col1_path == "models/customers.yml"

    def test_exposure_different_from_model(self):
        """Test that exposures and models use different directories."""
        path_builder = DbtPathBuilder({})

        model_path = path_builder.get_path("model.my_project.dashboard", ItemType.TABLE)
        exposure_path = path_builder.get_path("exposure.my_project.dashboard", ItemType.DOC)

        assert model_path != exposure_path
        assert "models/" in model_path
        assert "exposures/" in exposure_path
