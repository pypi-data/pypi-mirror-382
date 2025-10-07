from pathlib import Path
from typing import Dict, List

from datadict_connector_base import (
    ChangeApplier,
    ChangeType,
    ItemChange,
    ItemType,
    PhysicalChangeRequest,
)
from ruamel.yaml import YAML

from .dbt_keys import is_column_key, parse_dbt_key
from .dbt_path_builder import DbtPathBuilder


class DbtApplier(ChangeApplier):
    """
    DBT change applier that converts ItemChange objects into file operations.
    Returns PhysicalChangeRequest objects without executing them.
    """

    def __init__(self):
        self.yaml = YAML()
        self.yaml.default_flow_style = False

    def _load_yaml(self, catalog_root: Path | None, relative_path: str) -> Dict:
        """Load existing YAML content if available."""
        if catalog_root is None:
            return {}

        file_path = catalog_root / relative_path
        if not file_path.exists():
            return {}

        with file_path.open("r", encoding="utf-8") as handle:
            data = self.yaml.load(handle) or {}

        if isinstance(data, dict):
            return data

        return {}

    def apply_change(
        self, change: ItemChange, lookup_table: Dict[str, str]
    ) -> List[PhysicalChangeRequest]:
        """
        Convert an ItemChange into physical file change requests.

        Args:
            change: The change to apply
            lookup_table: Dict mapping FQN keys to existing file paths

        Returns:
            List of PhysicalChangeRequest objects
        """
        if not change.key:
            raise ValueError("Change key is required")

        path_builder = DbtPathBuilder(lookup_table)
        catalog_root_value = lookup_table.get("__catalog_root__")
        catalog_root = Path(catalog_root_value) if catalog_root_value else None
        resource_type, parts = parse_dbt_key(change.key)

        if not resource_type or parts is None:
            raise ValueError(f"Invalid DBT key: {change.key}")

        # Determine item type for path generation
        if resource_type == "model" or resource_type == "seed":
            item_type = ItemType.TABLE
        elif resource_type == "exposure":
            item_type = ItemType.DOC
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")

        if resource_type == "model":
            if is_column_key(change.key):
                return self._apply_column_change(change, path_builder, item_type, catalog_root)
            else:
                return self._apply_model_change(change, path_builder, item_type, catalog_root)
        elif resource_type == "exposure":
            return self._apply_exposure_change(change, path_builder, item_type, catalog_root)
        elif resource_type == "seed":
            if is_column_key(change.key):
                return self._apply_column_change(
                    change, path_builder, ItemType.TABLE, catalog_root
                )
            else:
                return self._apply_seed_change(change, path_builder, item_type, catalog_root)
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")

    def _apply_model_change(
        self,
        change: ItemChange,
        path_builder: DbtPathBuilder,
        item_type: ItemType,
        catalog_root: Path | None,
    ) -> List[PhysicalChangeRequest]:
        """Apply change to model file."""
        path = path_builder.get_path(change.key, item_type)
        parts = change.key.split(".")[1:]
        package_name = parts[0] if len(parts) > 0 else "unknown"
        model_name = parts[1] if len(parts) > 1 else "unknown"

        data = self._load_yaml(catalog_root, path)

        if change.change == ChangeType.CREATE:
            data.setdefault("name", model_name)
            data.setdefault("metadata", {"package_name": package_name})
            metadata = data.get("metadata")
            if isinstance(metadata, dict):
                metadata.setdefault("package_name", package_name)
            else:
                data["metadata"] = {"package_name": package_name}
            columns = data.get("columns")
            if not isinstance(columns, list):
                data["columns"] = []
            if change.name and change.name != model_name:
                data["description"] = change.name
            data["archived"] = False

        elif change.change == ChangeType.MODIFY:
            if change.name:
                data["description"] = change.name

        elif change.change in (ChangeType.ARCHIVE, ChangeType.UNARCHIVE):
            archived = change.change == ChangeType.ARCHIVE
            if archived:
                data["archived"] = True
            else:
                data.pop("archived", None)

        # Convert to YAML string
        from io import StringIO

        stream = StringIO()
        self.yaml.dump(data, stream)
        content = stream.getvalue()

        return [PhysicalChangeRequest(path=path, action="set", content=content)]

    def _apply_exposure_change(
        self,
        change: ItemChange,
        path_builder: DbtPathBuilder,
        item_type: ItemType,
        catalog_root: Path | None,
    ) -> List[PhysicalChangeRequest]:
        """Apply change to exposure file."""
        path = path_builder.get_path(change.key, item_type)
        parts = change.key.split(".")[1:]
        package_name = parts[0] if len(parts) > 0 else "unknown"
        exposure_name = parts[1] if len(parts) > 1 else "unknown"

        data = self._load_yaml(catalog_root, path)

        if change.change == ChangeType.CREATE:
            data.setdefault("name", exposure_name)
            data["type"] = change.sub_type or data.get("type") or "dashboard"
            metadata = data.get("metadata")
            if isinstance(metadata, dict):
                metadata.setdefault("package_name", package_name)
            else:
                data["metadata"] = {"package_name": package_name}
            if change.name and change.name != exposure_name:
                data["description"] = change.name
            data["archived"] = False

        elif change.change == ChangeType.MODIFY:
            if change.name:
                data["description"] = change.name
            if change.sub_type:
                data["type"] = change.sub_type

        elif change.change in (ChangeType.ARCHIVE, ChangeType.UNARCHIVE):
            archived = change.change == ChangeType.ARCHIVE
            if archived:
                data["archived"] = True
            else:
                data.pop("archived", None)

        # Convert to YAML string
        from io import StringIO

        stream = StringIO()
        self.yaml.dump(data, stream)
        content = stream.getvalue()

        return [PhysicalChangeRequest(path=path, action="set", content=content)]

    def _apply_seed_change(
        self,
        change: ItemChange,
        path_builder: DbtPathBuilder,
        item_type: ItemType,
        catalog_root: Path | None,
    ) -> List[PhysicalChangeRequest]:
        """Apply change to seed file."""
        path = path_builder.get_path(change.key, item_type)
        parts = change.key.split(".")[1:]
        package_name = parts[0] if len(parts) > 0 else "unknown"
        seed_name = parts[1] if len(parts) > 1 else "unknown"

        data = self._load_yaml(catalog_root, path)

        if change.change == ChangeType.CREATE:
            data.setdefault("name", seed_name)
            metadata = data.get("metadata")
            if isinstance(metadata, dict):
                metadata.setdefault("package_name", package_name)
            else:
                data["metadata"] = {"package_name": package_name}
            columns = data.get("columns")
            if not isinstance(columns, list):
                data["columns"] = []
            if change.name and change.name != seed_name:
                data["description"] = change.name
            data["archived"] = False

        elif change.change == ChangeType.MODIFY:
            if change.name:
                data["description"] = change.name

        elif change.change in (ChangeType.ARCHIVE, ChangeType.UNARCHIVE):
            archived = change.change == ChangeType.ARCHIVE
            if archived:
                data["archived"] = True
            else:
                data.pop("archived", None)

        # Convert to YAML string
        from io import StringIO

        stream = StringIO()
        self.yaml.dump(data, stream)
        content = stream.getvalue()

        return [PhysicalChangeRequest(path=path, action="set", content=content)]

    def _apply_column_change(
        self,
        change: ItemChange,
        path_builder: DbtPathBuilder,
        item_type: ItemType,
        catalog_root: Path | None,
    ) -> List[PhysicalChangeRequest]:
        """Apply change to column in parent file."""
        # Get parent key to find the file
        parts = change.key.split(".")
        if len(parts) < 4:
            raise ValueError(f"Invalid column key: {change.key}")

        column_name = parts[-1]
        parent_key = ".".join(parts[:-1])

        path = path_builder.get_path(parent_key, item_type)
        data = self._load_yaml(catalog_root, path)

        columns = data.get("columns")
        if not isinstance(columns, list):
            columns = []
            data["columns"] = columns

        existing_col = None
        for col in columns:
            if isinstance(col, dict) and col.get("name") == column_name:
                existing_col = col
                break

        if change.change == ChangeType.CREATE:
            if existing_col is None:
                existing_col = {
                    "name": column_name,
                    "data_type": change.data_type or "string",
                    "archived": False,
                }
                if change.name and change.name != column_name:
                    existing_col["description"] = change.name
                columns.append(existing_col)
            else:
                if change.name and change.name != column_name:
                    existing_col["description"] = change.name
                if change.data_type:
                    existing_col["data_type"] = change.data_type
                else:
                    existing_col.setdefault("data_type", "string")
                existing_col["archived"] = False

        elif change.change == ChangeType.MODIFY:
            if existing_col is None:
                return []
            if change.name and change.name != column_name:
                existing_col["description"] = change.name
            if change.data_type:
                existing_col["data_type"] = change.data_type

        elif change.change in (ChangeType.ARCHIVE, ChangeType.UNARCHIVE):
            if existing_col is None:
                return []
            archived = change.change == ChangeType.ARCHIVE
            if archived:
                existing_col["archived"] = True
            else:
                existing_col.pop("archived", None)

        # Convert to YAML string
        from io import StringIO

        stream = StringIO()
        self.yaml.dump(data, stream)
        content = stream.getvalue()

        return [PhysicalChangeRequest(path=path, action="set", content=content)]
