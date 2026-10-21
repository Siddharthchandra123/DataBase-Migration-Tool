from fastapi import FastAPI

from app.api.audit import router as audit_router
from app.api.connections import router as connections_router
from app.api.discovery import router as discovery_router
from app.api.migrations import router as migrations_router
from app.api.schema_mapping import router as schema_mapping_router
from app.api.validation import router as validation_router
from app.core.config import settings
from app.core.database import init_db

app = FastAPI(
    title=settings.app_name,
    version="0.4.0",
    description="Enterprise database migration platform MVP",
)

app.include_router(connections_router, prefix="/api/connections", tags=["Connections"])
app.include_router(discovery_router, prefix="/api/discovery", tags=["Discovery"])
app.include_router(schema_mapping_router, prefix="/api/schema", tags=["Schema Mapping"])
app.include_router(validation_router, prefix="/api/validation", tags=["Validation"])
app.include_router(audit_router, prefix="/api/audit", tags=["Audit"])
app.include_router(migrations_router, prefix="/api/migrations", tags=["Migrations"])


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name, "version": "0.4.0"}
