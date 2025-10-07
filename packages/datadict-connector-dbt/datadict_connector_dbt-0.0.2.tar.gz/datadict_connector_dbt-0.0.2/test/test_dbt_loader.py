"""
Tests for DBT catalog loader.
"""

from datadict_connector_base import ItemType
from datadict_connector_dbt import DbtLoader
from datadict_connector_dbt.dbt_types import DbtSubType


class TestDbtLoader:
    """Test DBT loader functionality."""

    def test_create_loader(self):
        """Test creating a loader instance."""
        loader = DbtLoader()
        assert loader is not None

    def test_load_empty_files(self):
        """Test loading from empty file dict."""
        loader = DbtLoader()
        items = loader.load_from_files({})
        assert items == []

    def test_load_model_with_columns(self):
        """Test loading a model with columns."""
        loader = DbtLoader()
        files = {
            "models/customers.yml": """
name: customers
metadata:
  package_name: my_project
  database: analytics
  schema: public
description: Customer dimension table
columns:
  - name: customer_id
    data_type: integer
    description: Primary key
  - name: email
    data_type: varchar
    description: Customer email
  - name: created_at
    data_type: timestamp
"""
        }

        items = loader.load_from_files(files)

        # Should have 1 model + 3 columns = 4 items
        assert len(items) == 4

        # Check model
        model_items = [i for i in items if i.type == ItemType.TABLE]
        assert len(model_items) == 1
        model = model_items[0]
        assert model.name == "customers"
        assert model.key == "model.my_project.customers"
        assert model.sub_type == DbtSubType.MODEL
        assert model.description == "Customer dimension table"

        # Check columns
        column_items = [i for i in items if i.type == ItemType.COLUMN]
        assert len(column_items) == 3
        column_names = {c.name for c in column_items}
        assert column_names == {"customer_id", "email", "created_at"}

    def test_load_exposure(self):
        """Test loading an exposure."""
        loader = DbtLoader()
        files = {
            "exposures/sales_dashboard.yml": """
name: sales_dashboard
type: dashboard
description: Sales performance dashboard
url: https://app.example.com/dashboards/sales
owner: data-team@example.com
metadata:
  package_name: my_project
"""
        }

        items = loader.load_from_files(files)

        # Should have 1 exposure
        assert len(items) == 1
        exposure = items[0]
        assert exposure.name == "sales_dashboard"
        assert exposure.key == "exposure.my_project.sales_dashboard"
        assert exposure.type == ItemType.DOC
        assert exposure.sub_type == DbtSubType.EXPOSURE
        assert exposure.description == "Sales performance dashboard"
        assert exposure.properties.get("url") == "https://app.example.com/dashboards/sales"

    def test_load_seed_with_columns(self):
        """Test loading a seed with columns."""
        loader = DbtLoader()
        files = {
            "seed/countries.yml": """
name: countries
metadata:
  package_name: my_project
description: Country reference data
columns:
  - name: country_code
    data_type: varchar
    description: ISO country code
  - name: country_name
    data_type: varchar
"""
        }

        items = loader.load_from_files(files)

        # Should have 1 seed + 2 columns = 3 items
        assert len(items) == 3

        # Check seed
        seed_items = [i for i in items if i.sub_type == DbtSubType.SEED]
        assert len(seed_items) == 1
        seed = seed_items[0]
        assert seed.name == "countries"
        assert seed.key == "seed.my_project.countries"
        assert seed.type == ItemType.TABLE

        # Check columns
        column_items = [i for i in items if i.type == ItemType.COLUMN]
        assert len(column_items) == 2

    def test_load_multiple_models(self):
        """Test loading multiple models."""
        loader = DbtLoader()
        files = {
            "models/customers.yml": """
name: customers
metadata:
  package_name: my_project
columns:
  - name: id
    data_type: integer
""",
            "models/orders.yml": """
name: orders
metadata:
  package_name: my_project
columns:
  - name: order_id
    data_type: integer
  - name: customer_id
    data_type: integer
""",
        }

        items = loader.load_from_files(files)

        # Should have 2 models + 3 columns = 5 items
        model_items = [i for i in items if i.type == ItemType.TABLE]
        assert len(model_items) == 2
        model_names = {m.name for m in model_items}
        assert model_names == {"customers", "orders"}

        # Check columns
        column_items = [i for i in items if i.type == ItemType.COLUMN]
        assert len(column_items) == 3

    def test_column_parent_keys(self):
        """Test that columns have correct parent keys."""
        loader = DbtLoader()
        files = {
            "models/users.yml": """
name: users
metadata:
  package_name: my_project
columns:
  - name: user_id
    data_type: integer
"""
        }

        items = loader.load_from_files(files)

        model = next(i for i in items if i.type == ItemType.TABLE)
        column = next(i for i in items if i.type == ItemType.COLUMN)

        assert column.parent_key == model.key
        assert column.key == f"{model.key}.{column.name}"

    def test_archived_flag(self):
        """Test that archived flag is properly loaded."""
        loader = DbtLoader()
        files = {
            "models/deprecated.yml": """
name: deprecated
metadata:
  package_name: my_project
archived: true
columns:
  - name: id
    data_type: integer
    archived: true
"""
        }

        items = loader.load_from_files(files)

        model = next(i for i in items if i.type == ItemType.TABLE)
        assert model.archived is True

        column = next(i for i in items if i.type == ItemType.COLUMN)
        assert column.archived is True

    def test_skip_non_model_files_in_models_dir(self):
        """Test that non-model files in models/ are skipped."""
        loader = DbtLoader()
        files = {
            "models/README.md": "# Models",
            "models/docs.md": "Documentation",
            "models/customers.yml": """
name: customers
metadata:
  package_name: my_project
columns: []
""",
        }

        items = loader.load_from_files(files)

        # Should only load the valid model
        model_items = [i for i in items if i.type == ItemType.TABLE]
        assert len(model_items) == 1
        assert model_items[0].name == "customers"

    def test_skip_invalid_yaml(self):
        """Test that invalid YAML files are skipped."""
        loader = DbtLoader()
        files = {
            "models/invalid.yml": "not: [valid yaml structure",
            "models/customers.yml": """
name: customers
metadata:
  package_name: my_project
columns: []
""",
        }

        items = loader.load_from_files(files)

        # Should only load the valid model
        model_items = [i for i in items if i.type == ItemType.TABLE]
        assert len(model_items) == 1
        assert model_items[0].name == "customers"

    def test_file_path_tracking(self):
        """Test that items track which file they came from."""
        loader = DbtLoader()
        files = {
            "models/customers.yml": """
name: customers
metadata:
  package_name: my_project
columns:
  - name: id
    data_type: integer
"""
        }

        items = loader.load_from_files(files)

        # All items should track the file path
        for item in items:
            assert item.file_path == "models/customers.yml"

    def test_dependency_order(self):
        """Test that items are returned in dependency order."""
        loader = DbtLoader()
        files = {
            "models/customers.yml": """
name: customers
metadata:
  package_name: my_project
columns:
  - name: id
    data_type: integer
"""
        }

        items = loader.load_from_files(files)

        # Model should come before columns
        types_in_order = [item.type for item in items]
        table_idx = types_in_order.index(ItemType.TABLE)
        column_indices = [i for i, t in enumerate(types_in_order) if t == ItemType.COLUMN]

        for col_idx in column_indices:
            assert table_idx < col_idx

    def test_mixed_resource_types(self):
        """Test loading models, exposures, and seeds together."""
        loader = DbtLoader()
        files = {
            "models/customers.yml": """
name: customers
metadata:
  package_name: my_project
columns:
  - name: id
    data_type: integer
""",
            "exposures/dashboard.yml": """
name: dashboard
type: dashboard
metadata:
  package_name: my_project
""",
            "seed/countries.yml": """
name: countries
metadata:
  package_name: my_project
columns:
  - name: code
    data_type: varchar
""",
        }

        items = loader.load_from_files(files)

        # Should have model, exposure, seed, and columns
        model_items = [i for i in items if i.sub_type == DbtSubType.MODEL]
        exposure_items = [i for i in items if i.sub_type == DbtSubType.EXPOSURE]
        seed_items = [i for i in items if i.sub_type == DbtSubType.SEED]

        assert len(model_items) == 1
        assert len(exposure_items) == 1
        assert len(seed_items) == 1

    def test_notes_field(self):
        """Test that notes field is loaded."""
        loader = DbtLoader()
        files = {
            "models/customers.yml": """
name: customers
metadata:
  package_name: my_project
description: Customer table
notes: Additional implementation notes here
columns: []
"""
        }

        items = loader.load_from_files(files)

        model = items[0]
        assert model.notes == "Additional implementation notes here"
