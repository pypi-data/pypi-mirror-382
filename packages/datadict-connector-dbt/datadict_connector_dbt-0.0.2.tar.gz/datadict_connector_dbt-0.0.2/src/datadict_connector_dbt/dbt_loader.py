from typing import Dict, List

from datadict_connector_base import CatalogItem, CatalogLoaderV2, ItemType, parse_yaml_string

from .dbt_schemas import ExposureConfig, ModelConfig
from .dbt_types import DbtSubType


class DbtLoader(CatalogLoaderV2):
    """
    DBT catalog loader that loads items from YAML file contents.

    Supports loading models, exposures, and seeds.
    """

    def load_from_files(self, files: Dict[str, str]) -> List[CatalogItem]:
        """
        Load all DBT catalog items from file contents.

        Returns items in dependency order (parents before children):
        1. Models/Seeds/Exposures
        2. Columns

        Args:
            files: Dict mapping normalized paths to file contents
                   e.g., {"models/customers.yml": "...", "exposures/dashboard.yml": "..."}
        """
        items = []

        # Load models from models/ files
        items.extend(self._load_models(files))

        # Load exposures from exposures/ files
        items.extend(self._load_exposures(files))

        # Load seeds from seed/ files
        items.extend(self._load_seeds(files))

        return items

    def _load_models(self, files: Dict[str, str]) -> List[CatalogItem]:
        """Load model items from file contents."""
        items = []

        for file_path, content in files.items():
            # Only process files in models/ directory
            if not file_path.startswith("models/") or not file_path.endswith(".yml"):
                continue

            try:
                model_data = parse_yaml_string(content)

                # Check if this looks like a model file (has name and metadata)
                if not (
                    "name" in model_data and ("metadata" in model_data or "columns" in model_data)
                ):
                    continue

                # Parse as ModelConfig
                model_config = ModelConfig.model_validate(model_data)

                # Generate model key
                package_name = (
                    getattr(model_config.metadata, "package_name", None)
                    if model_config.metadata
                    else None
                ) or "default"
                model_key = f"model.{package_name}.{model_config.name}"

                # Create model item
                model_item = CatalogItem(
                    name=model_config.name,
                    key=model_key,
                    type=ItemType.TABLE,
                    sub_type=DbtSubType.MODEL,
                    description=model_config.description,
                    notes=model_config.notes,
                    archived=model_config.archived or False,
                    properties={"fullQualifiedName": model_key},
                    file_path=file_path,
                )
                items.append(model_item)

                # Create column items
                for column_config in model_config.columns:
                    column_key = f"{model_key}.{column_config.name}"

                    column_item = CatalogItem(
                        name=column_config.name,
                        key=column_key,
                        parent_key=model_key,
                        type=ItemType.COLUMN,
                        sub_type=DbtSubType.COLUMN,
                        data_type=column_config.data_type,
                        description=column_config.description,
                        archived=column_config.archived or False,
                        properties={"fullQualifiedName": column_key},
                        file_path=file_path,
                    )
                    items.append(column_item)

            except Exception:
                # If parsing fails, skip this file
                continue

        return items

    def _load_exposures(self, files: Dict[str, str]) -> List[CatalogItem]:
        """Load exposure items from file contents."""
        items = []

        for file_path, content in files.items():
            # Only process files in exposures/ directory
            if not file_path.startswith("exposures/") or not file_path.endswith(".yml"):
                continue

            try:
                exposure_data = parse_yaml_string(content)

                # Check if this looks like an exposure file (has name and type)
                if not ("name" in exposure_data and "type" in exposure_data):
                    continue

                # Parse as ExposureConfig
                exposure_config = ExposureConfig.model_validate(exposure_data)

                # Generate exposure key
                package_name = (
                    getattr(exposure_config.metadata, "package_name", "default")
                    if exposure_config.metadata
                    else "default"
                )
                exposure_key = f"exposure.{package_name}.{exposure_config.name}"

                # Create exposure item
                exposure_item = CatalogItem(
                    name=exposure_config.name,
                    key=exposure_key,
                    type=ItemType.DOC,
                    sub_type=DbtSubType.EXPOSURE,
                    description=exposure_config.description,
                    notes=exposure_config.notes,
                    archived=exposure_config.archived or False,
                    properties={
                        "fullQualifiedName": exposure_key,
                        "exposureType": exposure_config.type,
                        "url": exposure_config.url,
                        "owner": exposure_config.owner,
                    },
                    file_path=file_path,
                )
                items.append(exposure_item)

            except Exception:
                # If parsing fails, skip this file
                continue

        return items

    def _load_seeds(self, files: Dict[str, str]) -> List[CatalogItem]:
        """Load seed items from file contents."""
        items = []

        for file_path, content in files.items():
            # Only process files in seed/ directory
            if not file_path.startswith("seed/") or not file_path.endswith(".yml"):
                continue

            try:
                seed_data = parse_yaml_string(content)

                # Check if this looks like a seed file (has name and columns)
                if not (
                    "name" in seed_data and ("metadata" in seed_data or "columns" in seed_data)
                ):
                    continue

                # Parse as ModelConfig (seeds use same structure as models)
                seed_config = ModelConfig.model_validate(seed_data)

                # Generate seed key
                package_name = (
                    getattr(seed_config.metadata, "package_name", None)
                    if seed_config.metadata
                    else None
                ) or "default"
                seed_key = f"seed.{package_name}.{seed_config.name}"

                # Create seed item
                seed_item = CatalogItem(
                    name=seed_config.name,
                    key=seed_key,
                    type=ItemType.TABLE,
                    sub_type=DbtSubType.SEED,
                    description=seed_config.description,
                    notes=seed_config.notes,
                    archived=seed_config.archived or False,
                    properties={"fullQualifiedName": seed_key},
                    file_path=file_path,
                )
                items.append(seed_item)

                # Create column items for seeds
                for column_config in seed_config.columns:
                    column_key = f"{seed_key}.{column_config.name}"

                    column_item = CatalogItem(
                        name=column_config.name,
                        key=column_key,
                        parent_key=seed_key,
                        type=ItemType.COLUMN,
                        sub_type=DbtSubType.COLUMN,
                        data_type=column_config.data_type,
                        description=column_config.description,
                        archived=column_config.archived or False,
                        properties={"fullQualifiedName": column_key},
                        file_path=file_path,
                    )
                    items.append(column_item)

            except Exception:
                # If parsing fails, skip this file
                continue

        return items
