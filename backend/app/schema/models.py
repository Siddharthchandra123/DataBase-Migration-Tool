from pydantic import BaseModel


class ColumnMetadata(BaseModel):
    name: str
    source_type: str
    nullable: bool = True
    ordinal_position: int
    length: int | None = None
    precision: int | None = None
    scale: int | None = None


class TableMetadata(BaseModel):
    schema_name: str
    table_name: str
    columns: list[ColumnMetadata]
