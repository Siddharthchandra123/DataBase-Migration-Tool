from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.schema.ddl import generate_postgres_ddl
from app.schema.models import ColumnMetadata, TableMetadata
from app.schema.type_mapping import map_db2_type

router = APIRouter()


class TypeMappingRequest(BaseModel):
    source_type: str
    length: int | None = None
    precision: int | None = None
    scale: int | None = None


class DDLRequest(BaseModel):
    schema_name: str
    table_name: str
    columns: list[ColumnMetadata]


@router.post("/type")
def map_type(request: TypeMappingRequest):
    try:
        target = map_db2_type(
            request.source_type,
            request.length,
            request.precision,
            request.scale,
        )
        return {
            "source_type": request.source_type,
            "target_type": target.name,
            "length": target.length,
            "precision": target.precision,
            "scale": target.scale,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/ddl")
def generate_ddl(request: DDLRequest):
    try:
        table = TableMetadata(
            schema_name=request.schema_name,
            table_name=request.table_name,
            columns=request.columns,
        )
        return {"ddl": generate_postgres_ddl(table)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
