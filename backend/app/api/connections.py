from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.connectors.base import ConnectionConfig
from app.connectors.factory import create_connector

router = APIRouter()


class ConnectionRequest(BaseModel):
    engine: str
    host: str
    port: int = Field(gt=0, lt=65536)
    database: str
    username: str
    password: str


@router.post("/test")
def test_connection(request: ConnectionRequest):
    connector = create_connector(ConnectionConfig(**request.model_dump()))
    try:
        return {"engine": request.engine, "connected": connector.test_connection()}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/supported")
def supported_databases():
    return {
        "databases": [
            {"engine": "db2", "status": "available"},
            {"engine": "postgresql", "status": "available"},
            {"engine": "oracle", "status": "planned"},
            {"engine": "mysql", "status": "planned"},
            {"engine": "sqlserver", "status": "planned"},
            {"engine": "sap_hana", "status": "planned"},
        ]
    }
