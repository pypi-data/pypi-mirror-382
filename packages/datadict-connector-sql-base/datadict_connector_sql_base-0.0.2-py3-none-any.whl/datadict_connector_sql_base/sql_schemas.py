from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ColumnConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    type: str
    description: Optional[str] = None
    archived: Optional[bool] = False


class Metadata(BaseModel):
    model_config = ConfigDict(extra="allow")

    database: str
    schema_name: str = Field(alias="schema")
    table_type: Optional[str] = Field(default=None, alias="tableType")


class TableConfig(BaseModel):
    """
    Table yaml files for database catalogs
    """

    model_config = ConfigDict(extra="allow")

    name: str
    metadata: Metadata
    description: Optional[str] = None
    notes: Optional[str] = None
    columns: list[ColumnConfig] = []
    archived: Optional[bool] = False


class SchemaItemConfig(BaseModel):
    """
    Schema yaml files for database schemas
    """

    model_config = ConfigDict(extra="allow")

    name: str
    description: Optional[str] = None
    notes: Optional[str] = None
    archived: Optional[bool] = False


class DatabaseItemConfig(BaseModel):
    """
    Configuration for databases
    """

    model_config = ConfigDict(extra="allow")
    schemas: list[SchemaItemConfig] = []

    name: str
    description: Optional[str] = None
    notes: Optional[str] = None
    archived: Optional[bool] = False


class DatabaseConfig(BaseModel):
    databases: list[DatabaseItemConfig] = []

