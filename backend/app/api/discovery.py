from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.connectors.base import ConnectionConfig
from app.connectors.factory import create_connector

router = APIRouter()


class DiscoveryRequest(BaseModel):
    engine: str
    host: str
    port: int
    database: str
    username: str
    password: str


def connector_for(request: DiscoveryRequest):
    return create_connector(ConnectionConfig(**request.model_dump()))


@router.post("/schemas")
def discover_schemas(request: DiscoveryRequest):
    connector = connector_for(request)
    try:
        return {"schemas": connector.get_schemas()}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        connector.close()


@router.post("/tables")
def discover_tables(request: DiscoveryRequest, schema: str):
    connector = connector_for(request)
    try:
        return {"schema": schema, "tables": connector.get_tables(schema)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        connector.close()


@router.post("/columns")
def discover_columns(request: DiscoveryRequest, schema: str, table: str):
    connector = connector_for(request)
    try:
        return {
            "schema": schema,
            "table": table,
            "columns": connector.get_columns(schema, table),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        connector.close()


@router.post("/constraints")
def discover_constraints(request: DiscoveryRequest, schema: str, table: str):
    connector = connector_for(request)

    if not hasattr(connector, "get_primary_keys"):
        raise HTTPException(
            status_code=400,
            detail=f"{request.engine} connector does not expose constraints yet",
        )

    try:
        return {
            "schema": schema,
            "table": table,
            "primary_keys": connector.get_primary_keys(schema, table),
            "foreign_keys": connector.get_foreign_keys(schema, table),
            "indexes": connector.get_indexes(schema, table),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        connector.close()
