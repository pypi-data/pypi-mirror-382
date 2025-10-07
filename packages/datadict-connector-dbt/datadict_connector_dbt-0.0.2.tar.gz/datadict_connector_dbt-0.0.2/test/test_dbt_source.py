"""
Tests for DBT manifest source.
"""

import pandas as pd
import pytest
from datadict_connector_dbt import DbtManifestSource


class TestDbtManifestSource:
    """Test DBT manifest source functionality."""

    def test_create_source(self):
        """Test creating a DBT manifest source."""
        source = DbtManifestSource()
        assert source is not None
        assert source.manifest_path is None
        assert source.manifest_data is None

    def test_set_credentials(self, manifest_credentials):
        """Test setting credentials with manifest path."""
        source = DbtManifestSource()
        source.set_credentials(manifest_credentials)
        assert source.manifest_path is not None
        assert source.manifest_data is not None

    def test_set_credentials_missing_path(self):
        """Test error when manifest_path not in credentials."""
        source = DbtManifestSource()
        with pytest.raises(ValueError, match="manifest_path"):
            source.set_credentials({})

    def test_set_credentials_nonexistent_file(self):
        """Test error when manifest file doesn't exist."""
        source = DbtManifestSource()
        with pytest.raises(FileNotFoundError):
            source.set_credentials({"manifest_path": "/nonexistent/manifest.json"})

    def test_read_metadata_structure(self, manifest_credentials):
        """Test reading metadata returns correct DataFrame structure."""
        source = DbtManifestSource()
        source.set_credentials(manifest_credentials)

        df = source.read_metadata()

        # Verify DataFrame structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

        # Verify required columns
        required_columns = {"type", "name", "key", "sub_type", "data_type", "parent_key"}
        assert required_columns.issubset(df.columns)

    def test_read_metadata_contains_models(self, manifest_credentials):
        """Test that metadata contains models."""
        source = DbtManifestSource()
        source.set_credentials(manifest_credentials)

        df = source.read_metadata()

        # Should have models
        model_items = df[df["sub_type"] == "model"]
        assert len(model_items) > 0

        # Check model structure
        for _, model in model_items.iterrows():
            assert model["type"] == "table"
            assert model["key"].startswith("model.")
            assert pd.isna(model["parent_key"])  # Models don't have parents

    def test_read_metadata_contains_seeds(self, manifest_credentials):
        """Test that metadata contains seeds."""
        source = DbtManifestSource()
        source.set_credentials(manifest_credentials)

        df = source.read_metadata()

        # Should have seeds
        seed_items = df[df["sub_type"] == "seed"]
        assert len(seed_items) > 0

        # Check seed structure
        for _, seed in seed_items.iterrows():
            assert seed["type"] == "table"
            assert seed["key"].startswith("seed.")

    def test_read_metadata_contains_exposures(self, manifest_credentials):
        """Test that metadata contains exposures."""
        source = DbtManifestSource()
        source.set_credentials(manifest_credentials)

        df = source.read_metadata()

        # Should have exposures
        exposure_items = df[df["sub_type"] == "exposure"]
        assert len(exposure_items) > 0

        # Check exposure structure
        for _, exposure in exposure_items.iterrows():
            assert exposure["type"] == "doc"
            assert exposure["key"].startswith("exposure.")

    def test_read_metadata_contains_columns(self, manifest_credentials):
        """Test that metadata contains columns."""
        source = DbtManifestSource()
        source.set_credentials(manifest_credentials)

        df = source.read_metadata()

        # Should have columns
        column_items = df[df["type"] == "column"]
        assert len(column_items) > 0

        # Check column structure
        for _, col in column_items.iterrows():
            assert col["sub_type"] == "column"
            assert col["parent_key"] is not None
            # Column key should have more parts than parent
            assert col["key"].count(".") > col["parent_key"].count(".")

    def test_column_parent_relationships(self, manifest_credentials):
        """Test that columns have correct parent relationships."""
        source = DbtManifestSource()
        source.set_credentials(manifest_credentials)

        df = source.read_metadata()

        # Get a model with columns
        model_items = df[(df["type"] == "table") & (df["sub_type"] == "model")]
        if len(model_items) > 0:
            model = model_items.iloc[0]
            model_key = model["key"]

            # Find columns for this model
            model_columns = df[df["parent_key"] == model_key]

            if len(model_columns) > 0:
                # Verify column keys are properly formed
                for _, col in model_columns.iterrows():
                    assert col["key"].startswith(model_key + ".")
                    assert col["type"] == "column"

    def test_unique_keys(self, manifest_credentials):
        """Test that all keys are unique."""
        source = DbtManifestSource()
        source.set_credentials(manifest_credentials)

        df = source.read_metadata()

        # Check for duplicate keys
        key_counts = df["key"].value_counts()
        duplicates = key_counts[key_counts > 1]
        assert len(duplicates) == 0, f"Found duplicate keys: {duplicates.index.tolist()}"

    def test_model_descriptions(self, manifest_credentials):
        """Test that model descriptions are extracted."""
        source = DbtManifestSource()
        source.set_credentials(manifest_credentials)

        df = source.read_metadata()

        # Check if description column exists
        model_items = df[df["sub_type"] == "model"]
        if len(model_items) > 0:
            # At least some models might have descriptions
            assert "description" in df.columns

    def test_close_clears_data(self, manifest_credentials):
        """Test that close() clears manifest data."""
        source = DbtManifestSource()
        source.set_credentials(manifest_credentials)

        # Load data
        df = source.read_metadata()
        assert len(df) > 0
        assert source.manifest_data is not None

        # Close
        source.close()
        assert source.manifest_data is None

    def test_read_without_credentials_fails(self):
        """Test that reading metadata without credentials fails."""
        source = DbtManifestSource()

        with pytest.raises(ValueError, match="Manifest not loaded"):
            source.read_metadata()

    def test_manifest_structure_validation(self, manifest_credentials):
        """Test that manifest has expected structure."""
        source = DbtManifestSource()
        source.set_credentials(manifest_credentials)

        # Verify manifest was loaded
        assert source.manifest_data is not None
        assert "nodes" in source.manifest_data
        assert isinstance(source.manifest_data["nodes"], dict)

    def test_column_data_types(self, manifest_credentials):
        """Test that column data types are extracted when available."""
        source = DbtManifestSource()
        source.set_credentials(manifest_credentials)

        df = source.read_metadata()

        # Check columns have data_type field
        column_items = df[df["type"] == "column"]
        if len(column_items) > 0:
            # data_type column should exist
            assert "data_type" in df.columns
