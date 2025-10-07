"""
Key generation and parsing functions for DBT catalog items.

These functions generate unique identifiers that match DBT's unique_id format
and can be used as key values for DataDict catalog items.
"""

from typing import List, Optional, Tuple


def dbt_key_model(package_name: str, model_name: str) -> str:
    """
    Generate unique key for DBT models.

    Format: model.{package_name}.{model_name}
    Example: model.my_dbt_project.stg_sales_customers
    """
    return f"model.{package_name}.{model_name}"


def dbt_key_exposure(package_name: str, exposure_name: str) -> str:
    """
    Generate unique key for DBT exposures.

    Format: exposure.{package_name}.{exposure_name}
    Example: exposure.my_dbt_project.weekly_sales_dashboard
    """
    return f"exposure.{package_name}.{exposure_name}"


def dbt_key_seed(package_name: str, seed_name: str) -> str:
    """
    Generate unique key for DBT seeds.

    Format: seed.{package_name}.{seed_name}
    Example: seed.my_dbt_project.countries
    """
    return f"seed.{package_name}.{seed_name}"


def dbt_key_column(parent_key: str, column_name: str) -> str:
    """
    Generate unique key for columns within DBT objects.

    Format: {parent_key}.{column_name}
    Example: model.my_dbt_project.stg_sales_customers.customer_id
    """
    return f"{parent_key}.{column_name}"


def dbt_key_from_unique_id(unique_id: str) -> str:
    """
    Extract or validate a DBT unique_id for use as a key.

    This function can be used when you already have a DBT unique_id
    and want to ensure it's in the correct format.
    """
    return unique_id


def dbt_key_from_fqn(resource_type: str, fqn: List[str]) -> str:
    """
    Generate key from DBT fully qualified name (fqn).

    Args:
        resource_type: The type of DBT resource (model, source, seed, etc.)
        fqn: List of name components from DBT manifest

    Example:
        fqn = ["my_dbt_project", "sales", "staging", "stg_sales_customers"]
        resource_type = "model"
        Returns: model.my_dbt_project.stg_sales_customers
    """
    if not fqn or len(fqn) < 2:
        raise ValueError(f"Invalid fqn for {resource_type}: {fqn}")

    package_name = fqn[0]
    object_name = fqn[-1]  # Last element is the actual object name

    return f"{resource_type}.{package_name}.{object_name}"


def parse_dbt_key(key: str) -> Tuple[Optional[str], Optional[List[str]]]:
    """
    Parse a DBT unique ID into resource type and parts.

    Args:
        key: DBT unique ID (e.g., "model.my_project.customers")

    Returns:
        Tuple of (resource_type, parts) or (None, None) if invalid

    Examples:
        "model.my_project.customers" -> ("model", ["my_project", "customers"])
        "seed.my_project.countries" -> ("seed", ["my_project", "countries"])
    """
    if not key or "." not in key:
        return None, None

    parts = key.split(".")
    if len(parts) < 3:  # Need at least: resource_type.package.name
        return None, None

    resource_type = parts[0]
    remaining_parts = parts[1:]

    return resource_type, remaining_parts


def is_column_key(key: str) -> bool:
    """
    Check if a key represents a column.

    Columns have the format: {parent_key}.{column_name}
    where parent_key is a valid DBT resource key.
    """
    parts = key.split(".")
    if len(parts) < 4:  # Need at least: resource_type.package.name.column
        return False

    # Check if the first 3+ parts form a valid DBT resource key
    potential_parent = ".".join(parts[:-1])
    resource_type, _ = parse_dbt_key(potential_parent)
    return resource_type is not None


def get_parent_key(key: str) -> Optional[str]:
    """
    Get the parent key for a column.

    Args:
        key: Column key (e.g., "model.my_project.customers.customer_id")

    Returns:
        Parent key (e.g., "model.my_project.customers") or None if invalid
    """
    if not is_column_key(key):
        return None

    parts = key.split(".")
    return ".".join(parts[:-1])


def slugify_filename(name: str) -> str:
    """
    Create a filesystem-safe filename from a DBT object name.

    Args:
        name: DBT object name

    Returns:
        Slugified filename suitable for YAML files
    """
    import re

    # Replace non-alphanumeric with underscores
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower())
    # Remove leading/trailing underscores
    slug = slug.strip("_")
    # Collapse multiple underscores
    slug = re.sub(r"_+", "_", slug)
    return slug
