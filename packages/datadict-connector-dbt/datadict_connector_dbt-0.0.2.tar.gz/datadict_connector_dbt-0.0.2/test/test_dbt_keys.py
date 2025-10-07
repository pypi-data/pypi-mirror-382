"""
Tests for DBT key generation and parsing utilities.
"""

from datadict_connector_dbt.dbt_keys import (
    dbt_key_column,
    dbt_key_exposure,
    dbt_key_model,
    dbt_key_seed,
    get_parent_key,
    is_column_key,
    parse_dbt_key,
    slugify_filename,
)


class TestDbtKeyGeneration:
    """Test DBT key generation functions."""

    def test_dbt_key_model(self):
        """Test generating model key."""
        key = dbt_key_model("my_project", "customers")
        assert key == "model.my_project.customers"

    def test_dbt_key_exposure(self):
        """Test generating exposure key."""
        key = dbt_key_exposure("my_project", "sales_dashboard")
        assert key == "exposure.my_project.sales_dashboard"

    def test_dbt_key_seed(self):
        """Test generating seed key."""
        key = dbt_key_seed("my_project", "countries")
        assert key == "seed.my_project.countries"

    def test_dbt_key_column(self):
        """Test generating column key."""
        parent_key = "model.my_project.customers"
        key = dbt_key_column(parent_key, "customer_id")
        assert key == "model.my_project.customers.customer_id"

    def test_key_formats_consistent(self):
        """Test that all key formats follow consistent pattern."""
        model_key = dbt_key_model("proj", "obj")
        exposure_key = dbt_key_exposure("proj", "obj")
        seed_key = dbt_key_seed("proj", "obj")

        # All should have 3 parts
        assert model_key.count(".") == 2
        assert exposure_key.count(".") == 2
        assert seed_key.count(".") == 2


class TestDbtKeyParsing:
    """Test DBT key parsing functions."""

    def test_parse_model_key(self):
        """Test parsing model key."""
        resource_type, parts = parse_dbt_key("model.my_project.customers")
        assert resource_type == "model"
        assert parts == ["my_project", "customers"]

    def test_parse_exposure_key(self):
        """Test parsing exposure key."""
        resource_type, parts = parse_dbt_key("exposure.my_project.dashboard")
        assert resource_type == "exposure"
        assert parts == ["my_project", "dashboard"]

    def test_parse_seed_key(self):
        """Test parsing seed key."""
        resource_type, parts = parse_dbt_key("seed.my_project.countries")
        assert resource_type == "seed"
        assert parts == ["my_project", "countries"]

    def test_parse_column_key(self):
        """Test parsing column key."""
        resource_type, parts = parse_dbt_key("model.my_project.customers.customer_id")
        assert resource_type == "model"
        assert parts == ["my_project", "customers", "customer_id"]

    def test_parse_invalid_key_no_dots(self):
        """Test parsing key without dots."""
        resource_type, parts = parse_dbt_key("invalid")
        assert resource_type is None
        assert parts is None

    def test_parse_invalid_key_too_few_parts(self):
        """Test parsing key with too few parts."""
        resource_type, parts = parse_dbt_key("model.project")
        assert resource_type is None
        assert parts is None

    def test_parse_empty_key(self):
        """Test parsing empty key."""
        resource_type, parts = parse_dbt_key("")
        assert resource_type is None
        assert parts is None


class TestColumnKeyIdentification:
    """Test column key identification functions."""

    def test_is_column_key_true(self):
        """Test identifying valid column keys."""
        assert is_column_key("model.my_project.customers.customer_id") is True
        assert is_column_key("seed.my_project.countries.country_code") is True

    def test_is_column_key_false_for_model(self):
        """Test that model keys are not column keys."""
        assert is_column_key("model.my_project.customers") is False

    def test_is_column_key_false_for_exposure(self):
        """Test that exposure keys are not column keys."""
        assert is_column_key("exposure.my_project.dashboard") is False

    def test_is_column_key_false_for_invalid(self):
        """Test that invalid keys are not column keys."""
        assert is_column_key("invalid.key") is False
        assert is_column_key("") is False

    def test_get_parent_key_for_column(self):
        """Test getting parent key from column key."""
        parent = get_parent_key("model.my_project.customers.customer_id")
        assert parent == "model.my_project.customers"

    def test_get_parent_key_for_seed_column(self):
        """Test getting parent key from seed column key."""
        parent = get_parent_key("seed.my_project.countries.country_code")
        assert parent == "seed.my_project.countries"

    def test_get_parent_key_for_non_column(self):
        """Test that non-column keys return None."""
        parent = get_parent_key("model.my_project.customers")
        assert parent is None

    def test_get_parent_key_for_invalid(self):
        """Test that invalid keys return None."""
        parent = get_parent_key("invalid.key")
        assert parent is None


class TestSlugifyFilename:
    """Test filename slugification."""

    def test_slugify_simple_name(self):
        """Test slugifying simple names."""
        assert slugify_filename("customers") == "customers"
        assert slugify_filename("orders") == "orders"

    def test_slugify_with_underscores(self):
        """Test that underscores are preserved."""
        assert slugify_filename("customer_orders") == "customer_orders"

    def test_slugify_with_spaces(self):
        """Test that spaces are converted to underscores."""
        slug = slugify_filename("customer orders")
        assert slug == "customer_orders"

    def test_slugify_with_special_chars(self):
        """Test that special characters are removed."""
        slug = slugify_filename("customer-orders!")
        assert "!" not in slug
        assert slug == "customer_orders"

    def test_slugify_uppercase(self):
        """Test that uppercase is converted to lowercase."""
        slug = slugify_filename("CustomerOrders")
        assert slug == "customerorders"

    def test_slugify_multiple_underscores(self):
        """Test that multiple underscores are collapsed."""
        slug = slugify_filename("customer___orders")
        assert slug == "customer_orders"

    def test_slugify_leading_trailing_underscores(self):
        """Test that leading/trailing underscores are trimmed."""
        slug = slugify_filename("_customers_")
        assert slug == "customers"

    def test_slugify_complex_name(self):
        """Test slugifying complex names."""
        slug = slugify_filename("My Complex Model Name!")
        assert slug == "my_complex_model_name"
        assert " " not in slug
        assert "!" not in slug

    def test_slugify_empty_string(self):
        """Test slugifying empty string."""
        slug = slugify_filename("")
        assert slug == ""

    def test_slugify_only_special_chars(self):
        """Test slugifying string with only special characters."""
        slug = slugify_filename("!!!---")
        assert slug == ""


class TestKeyRoundTrip:
    """Test that keys can be generated and parsed consistently."""

    def test_model_key_roundtrip(self):
        """Test model key generation and parsing roundtrip."""
        key = dbt_key_model("my_project", "customers")
        resource_type, parts = parse_dbt_key(key)

        assert resource_type == "model"
        assert parts[0] == "my_project"
        assert parts[1] == "customers"

    def test_exposure_key_roundtrip(self):
        """Test exposure key generation and parsing roundtrip."""
        key = dbt_key_exposure("my_project", "dashboard")
        resource_type, parts = parse_dbt_key(key)

        assert resource_type == "exposure"
        assert parts[0] == "my_project"
        assert parts[1] == "dashboard"

    def test_column_key_roundtrip(self):
        """Test column key generation and parsing roundtrip."""
        parent_key = dbt_key_model("my_project", "customers")
        column_key = dbt_key_column(parent_key, "customer_id")

        assert is_column_key(column_key)
        assert get_parent_key(column_key) == parent_key

    def test_nested_column_identification(self):
        """Test that deeply nested keys are handled correctly."""
        # Even with extra dots, should still identify as column
        key = "model.my_project.customers.nested.field"
        assert is_column_key(key)
        # Parent should be everything except last part
        parent = get_parent_key(key)
        assert parent == "model.my_project.customers.nested"
