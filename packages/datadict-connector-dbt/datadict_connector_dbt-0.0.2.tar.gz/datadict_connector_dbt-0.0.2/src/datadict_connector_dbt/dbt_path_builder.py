from typing import Dict

from datadict_connector_base import ItemType, PathBuilder

from .dbt_keys import get_parent_key, is_column_key, parse_dbt_key, slugify_filename


class DbtPathBuilder(PathBuilder):
    """
    Path builder for DBT catalogs.

    Default path structure:
    - models/{model_name}.yml: Individual model files
    - exposures/{exposure_name}.yml: Individual exposure files
    - seed/{seed_name}.yml: Individual seed files
    - Columns: Same file as parent object
    """

    def __init__(self, lookup_table: Dict[str, str]):
        super().__init__(lookup_table)

    def get_default_path(self, key: str, item_type: ItemType) -> str:
        """
        Generate the default physical YAML file path for a DBT catalog item.

        Path generation strategy based on DBT resource type:
        - models: models/{model_name}.yml
        - exposures: exposures/{exposure_name}.yml
        - seeds: seed/{seed_name}.yml
        - columns: same file as parent object
        """
        # Handle columns first - they use the same file as their parent object
        if is_column_key(key):
            parent_key = get_parent_key(key)
            if not parent_key:
                raise ValueError(f"Invalid column key: {key}")
            # Get parent's item type based on parent's resource type
            parent_resource_type, _ = parse_dbt_key(parent_key)
            parent_item_type = self._resource_type_to_item_type(parent_resource_type)
            return self.get_default_path(parent_key, parent_item_type)

        resource_type, parts = parse_dbt_key(key)
        if not resource_type or not parts:
            raise ValueError(f"Invalid DBT key: {key}")

        if resource_type == "model":
            return self._get_model_path(parts)
        elif resource_type == "exposure":
            return self._get_exposure_path(parts)
        elif resource_type == "seed":
            return self._get_seed_path(parts)
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")

    def _resource_type_to_item_type(self, resource_type: str | None) -> ItemType:
        """Convert DBT resource type to ItemType."""
        if resource_type == "model" or resource_type == "seed":
            return ItemType.TABLE
        elif resource_type == "exposure":
            return ItemType.DOC
        else:
            return ItemType.TABLE  # Default

    def _get_model_path(self, parts: list[str]) -> str:
        """
        Generate path for DBT models.

        Strategy: models/{safe_model_name}.yml
        """
        if len(parts) < 2:
            return "models/unknown.yml"

        # Use just the model name (last part) for the filename
        model_name = parts[-1]
        safe_name = slugify_filename(model_name)
        return f"models/{safe_name}.yml"

    def _get_exposure_path(self, parts: list[str]) -> str:
        """
        Generate path for DBT exposures.

        Strategy: exposures/{safe_exposure_name}.yml
        """
        if len(parts) < 2:
            return "exposures/unknown.yml"

        exposure_name = parts[-1]
        safe_name = slugify_filename(exposure_name)
        return f"exposures/{safe_name}.yml"

    def _get_seed_path(self, parts: list[str]) -> str:
        """
        Generate path for DBT seeds.

        Strategy: seed/{safe_seed_name}.yml
        """
        if len(parts) < 2:
            return "seed/unknown.yml"

        seed_name = parts[-1]
        safe_name = slugify_filename(seed_name)
        return f"seed/{safe_name}.yml"
