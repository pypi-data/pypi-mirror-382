"""
Tests for DBT change applier.
"""

import pytest
from datadict_connector_base import ChangeType, ItemChange, ItemType
from datadict_connector_dbt import DbtApplier


class TestDbtApplier:
    """Test DBT applier functionality."""

    def test_create_applier(self):
        """Test creating an applier instance."""
        applier = DbtApplier()
        assert applier is not None

    def test_create_model(self):
        """Test applying CREATE change for model."""
        applier = DbtApplier()
        change = ItemChange(
            key="model.my_project.customers",
            type=ItemType.TABLE,
            change=ChangeType.CREATE,
            name="Customer table",
        )

        requests = applier.apply_change(change, {})

        assert len(requests) == 1
        assert requests[0].path == "models/customers.yml"
        assert requests[0].action == "set"
        assert "name: customers" in requests[0].content
        assert "metadata:" in requests[0].content
        assert "package_name: my_project" in requests[0].content

    def test_create_exposure(self):
        """Test applying CREATE change for exposure."""
        applier = DbtApplier()
        change = ItemChange(
            key="exposure.my_project.sales_dashboard",
            type=ItemType.DOC,
            change=ChangeType.CREATE,
            name="Sales Dashboard",
            sub_type="dashboard",
        )

        requests = applier.apply_change(change, {})

        assert len(requests) == 1
        assert requests[0].path == "exposures/sales_dashboard.yml"
        assert requests[0].action == "set"
        assert "name: sales_dashboard" in requests[0].content
        assert "type: dashboard" in requests[0].content

    def test_create_seed(self):
        """Test applying CREATE change for seed."""
        applier = DbtApplier()
        change = ItemChange(
            key="seed.my_project.countries",
            type=ItemType.TABLE,
            change=ChangeType.CREATE,
            name="Country reference data",
        )

        requests = applier.apply_change(change, {})

        assert len(requests) == 1
        assert requests[0].path == "seed/countries.yml"
        assert requests[0].action == "set"
        assert "name: countries" in requests[0].content

    def test_create_column(self):
        """Test applying CREATE change for column."""
        applier = DbtApplier()
        change = ItemChange(
            key="model.my_project.customers.email",
            type=ItemType.COLUMN,
            change=ChangeType.CREATE,
            name="Email address",
            data_type="varchar",
        )

        requests = applier.apply_change(change, {})

        assert len(requests) == 1
        # Column should modify parent model file
        assert requests[0].path == "models/customers.yml"
        assert requests[0].action == "set"

    def test_modify_model(self):
        """Test applying MODIFY change for model."""
        applier = DbtApplier()
        change = ItemChange(
            key="model.my_project.customers",
            type=ItemType.TABLE,
            change=ChangeType.MODIFY,
            name="Updated description",
        )

        requests = applier.apply_change(change, {})

        assert len(requests) == 1
        assert requests[0].path == "models/customers.yml"
        assert "description:" in requests[0].content

    def test_archive_model(self):
        """Test applying ARCHIVE change for model."""
        applier = DbtApplier()
        change = ItemChange(
            key="model.my_project.customers",
            type=ItemType.TABLE,
            change=ChangeType.ARCHIVE,
        )

        requests = applier.apply_change(change, {})

        assert len(requests) == 1
        assert "archived: true" in requests[0].content or "archived:" in requests[0].content

    def test_unarchive_model(self):
        """Test applying UNARCHIVE change for model."""
        applier = DbtApplier()
        change = ItemChange(
            key="model.my_project.customers",
            type=ItemType.TABLE,
            change=ChangeType.UNARCHIVE,
        )

        requests = applier.apply_change(change, {})

        assert len(requests) == 1
        assert requests[0].path == "models/customers.yml"

    def test_lookup_table_used_for_paths(self):
        """Test that lookup table is used for path resolution."""
        applier = DbtApplier()
        lookup_table = {
            "model.my_project.customers": "custom/customers.yml",
        }

        change = ItemChange(
            key="model.my_project.customers",
            type=ItemType.TABLE,
            change=ChangeType.MODIFY,
            name="Updated",
        )

        requests = applier.apply_change(change, lookup_table)

        assert len(requests) == 1
        assert requests[0].path == "custom/customers.yml"

    def test_no_file_io_performed(self):
        """Test that applier does not perform file I/O."""
        applier = DbtApplier()
        change = ItemChange(
            key="model.my_project.customers",
            type=ItemType.TABLE,
            change=ChangeType.CREATE,
        )

        # Should not raise any file-related errors
        requests = applier.apply_change(change, {})

        # Should return requests, not execute them
        assert len(requests) > 0
        assert all(hasattr(r, "path") for r in requests)

    def test_returns_physical_change_requests(self):
        """Test that applier returns PhysicalChangeRequest objects."""
        applier = DbtApplier()
        change = ItemChange(
            key="model.my_project.customers",
            type=ItemType.TABLE,
            change=ChangeType.CREATE,
        )

        requests = applier.apply_change(change, {})

        assert len(requests) > 0
        for request in requests:
            assert hasattr(request, "path")
            assert hasattr(request, "action")
            assert hasattr(request, "content")
            assert isinstance(request.path, str)
            assert isinstance(request.action, str)
            assert isinstance(request.content, str)

    def test_missing_key_raises_error(self):
        """Test that missing key raises error."""
        applier = DbtApplier()
        change = ItemChange(
            key=None,
            type=ItemType.TABLE,
            change=ChangeType.CREATE,
        )

        with pytest.raises(ValueError, match="key is required"):
            applier.apply_change(change, {})

    def test_invalid_dbt_key_raises_error(self):
        """Test that invalid DBT key raises error."""
        applier = DbtApplier()
        change = ItemChange(
            key="invalid.key",
            type=ItemType.TABLE,
            change=ChangeType.CREATE,
        )

        with pytest.raises(ValueError, match="Invalid DBT key"):
            applier.apply_change(change, {})

    def test_unsupported_resource_type_raises_error(self):
        """Test that unsupported resource type raises error."""
        applier = DbtApplier()
        change = ItemChange(
            key="test.my_project.some_test",
            type=ItemType.TABLE,
            change=ChangeType.CREATE,
        )

        with pytest.raises(ValueError, match="Unsupported resource type"):
            applier.apply_change(change, {})

    def test_yaml_content_is_valid(self):
        """Test that generated YAML content is valid."""
        applier = DbtApplier()
        change = ItemChange(
            key="model.my_project.customers",
            type=ItemType.TABLE,
            change=ChangeType.CREATE,
            name="Customer accounts",
        )

        requests = applier.apply_change(change, {})

        # Should be valid YAML
        import yaml

        content = requests[0].content
        parsed = yaml.safe_load(content)
        assert isinstance(parsed, dict)
        assert "name" in parsed

    def test_seed_column_uses_parent_path(self):
        """Test that seed column changes use parent seed file path."""
        applier = DbtApplier()

        change = ItemChange(
            key="seed.my_project.countries.country_code",
            type=ItemType.COLUMN,
            change=ChangeType.CREATE,
            data_type="varchar",
        )

        requests = applier.apply_change(change, {})

        # Should modify parent seed file
        assert requests[0].path == "seed/countries.yml"

    def test_exposure_type_field(self):
        """Test that exposure type is included in YAML."""
        applier = DbtApplier()
        change = ItemChange(
            key="exposure.my_project.dashboard",
            type=ItemType.DOC,
            change=ChangeType.CREATE,
            sub_type="dashboard",
        )

        requests = applier.apply_change(change, {})

        assert "type: dashboard" in requests[0].content

    def test_modify_exposure_type(self):
        """Test modifying exposure type."""
        applier = DbtApplier()
        change = ItemChange(
            key="exposure.my_project.report",
            type=ItemType.DOC,
            change=ChangeType.MODIFY,
            sub_type="analysis",
        )

        requests = applier.apply_change(change, {})

        assert len(requests) == 1
        assert "type: analysis" in requests[0].content

    def test_column_data_type_preserved(self):
        """Test that column data type is preserved in YAML."""
        applier = DbtApplier()
        change = ItemChange(
            key="model.my_project.customers.email",
            type=ItemType.COLUMN,
            change=ChangeType.CREATE,
            data_type="varchar(255)",
        )

        requests = applier.apply_change(change, {})

        assert "data_type:" in requests[0].content

    def test_multiple_package_names(self):
        """Test changes for models in different packages."""
        applier = DbtApplier()

        change1 = ItemChange(
            key="model.project1.customers",
            type=ItemType.TABLE,
            change=ChangeType.CREATE,
        )

        change2 = ItemChange(
            key="model.project2.customers",
            type=ItemType.TABLE,
            change=ChangeType.CREATE,
        )

        requests1 = applier.apply_change(change1, {})
        requests2 = applier.apply_change(change2, {})

        # Both should use same path (only object name matters for path)
        # But metadata should differ
        assert "package_name: project1" in requests1[0].content
        assert "package_name: project2" in requests2[0].content
