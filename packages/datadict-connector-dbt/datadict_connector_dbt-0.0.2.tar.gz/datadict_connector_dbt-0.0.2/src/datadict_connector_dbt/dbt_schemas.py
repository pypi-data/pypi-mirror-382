"""
DBT YAML schemas for DataDict catalog items.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ColumnConfig(BaseModel):
    """Column configuration for DBT models and sources."""

    model_config = ConfigDict(extra="allow")

    name: str
    description: Optional[str] = None
    data_type: Optional[str] = None
    archived: Optional[bool] = False


class ModelMetadata(BaseModel):
    """Metadata for DBT models containing identifying information."""

    model_config = ConfigDict(extra="allow")

    file_path: Optional[str] = None
    database: Optional[str] = None
    schema_name: Optional[str] = Field(default=None, alias="schema")
    materialized: Optional[str] = None
    package_name: Optional[str] = None


class ModelConfig(BaseModel):
    """DBT model configuration schema."""

    model_config = ConfigDict(extra="allow")

    name: str
    description: Optional[str] = None
    notes: Optional[str] = None
    columns: List[ColumnConfig] = []
    metadata: ModelMetadata
    archived: Optional[bool] = False


class ExposureConfig(BaseModel):
    """DBT exposure configuration schema."""

    model_config = ConfigDict(extra="allow")

    name: str
    type: str  # dashboard, notebook, analysis, ml, application
    description: Optional[str] = None
    notes: Optional[str] = None
    url: Optional[str] = None
    owner: Optional[str] = None
    metadata: Optional[ModelMetadata] = None
    archived: Optional[bool] = False
