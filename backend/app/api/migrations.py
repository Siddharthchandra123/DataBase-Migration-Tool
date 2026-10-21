from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.connectors.base import ConnectionConfig
from app.connectors.factory import create_connector
from app.core.database import SessionLocal, get_db
from app.discovery.dependencies import ForeignKey, topological_sort
from app.migration.parallel import run_parallel
from app.migration.planner import build_plan
from app.migration.runner import run_migration
from app.models.migration import MigrationJob

router = APIRouter()


class MigrationCreateRequest(BaseModel):
    name: str
    source_engine: str
    target_engine: str


class ConnectionBody(BaseModel):
    engine: str
    host: str
    port: int
    database: str
    username: str
    password: str


class PlanRequest(BaseModel):
    source: ConnectionBody
    source_schema: str
    target_schema: str = "public"


class DependencyPlanRequest(BaseModel):
    source: ConnectionBody
    source_schema: str
    target_schema: str = "public"


class RunMigrationRequest(BaseModel):
    source: ConnectionBody
    target: ConnectionBody
    source_schema: str
    target_schema: str = "public"
    tables: list[str] = Field(min_length=1)
    batch_size: int = Field(default=5000, ge=100, le=100000)
    max_workers: int = Field(default=1, ge=1, le=16)


@router.post("")
def create_migration(
    request: MigrationCreateRequest,
    db: Session = Depends(get_db),
):
    job = MigrationJob(
        name=request.name,
        source_engine=request.source_engine,
        target_engine=request.target_engine,
        status="CREATED",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"id": job.id, "name": job.name, "status": job.status}


@router.get("/{job_id}")
def get_migration(job_id: int, db: Session = Depends(get_db)):
    job = db.get(MigrationJob, job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")

    return {
        "id": job.id,
        "name": job.name,
        "source_engine": job.source_engine,
        "target_engine": job.target_engine,
        "status": job.status,
        "total_tables": job.total_tables,
        "completed_tables": job.completed_tables,
        "total_rows": job.total_rows,
        "migrated_rows": job.migrated_rows,
        "error_count": job.error_count,
        "error_message": job.error_message,
    }


@router.post("/plan")
def create_plan(request: PlanRequest):
    connector = create_connector(
        ConnectionConfig(**request.source.model_dump())
    )

    try:
        tables = connector.get_tables(request.source_schema)
        plan = build_plan(
            tables=tables,
            source_schema=request.source_schema,
            target_schema=request.target_schema,
        )
        return {
            "source_schema": request.source_schema,
            "target_schema": request.target_schema,
            "table_count": len(plan),
            "tasks": [task.__dict__ for task in plan],
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        connector.close()


@router.post("/plan/dependencies")
def create_dependency_plan(request: DependencyPlanRequest):
    connector = create_connector(
        ConnectionConfig(**request.source.model_dump())
    )

    try:
        tables = connector.get_tables(request.source_schema)
        foreign_keys = []

        if hasattr(connector, "get_foreign_keys"):
            for table in tables:
                for row in connector.get_foreign_keys(
                    request.source_schema,
                    table,
                ):
                    foreign_keys.append(
                        ForeignKey(
                            schema=row["schema"],
                            table=row["table"],
                            column=row["column_name"],
                            referenced_schema=row["referenced_schema"],
                            referenced_table=row["referenced_table"],
                            referenced_column=row["referenced_column"],
                        )
                    )

        ordered = topological_sort(tables, foreign_keys)

        return {
            "source_schema": request.source_schema,
            "target_schema": request.target_schema,
            "table_count": len(ordered),
            "execution_order": ordered,
            "dependencies": [
                {
                    "table": fk.table,
                    "column": fk.column,
                    "references": fk.referenced_table,
                    "referenced_column": fk.referenced_column,
                }
                for fk in foreign_keys
            ],
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        connector.close()


@router.post("/run")
def start_migration(
    request: RunMigrationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    job = MigrationJob(
        name=f'{request.source_schema} → {request.target_schema}',
        source_engine=request.source.engine,
        target_engine=request.target.engine,
        status="QUEUED",
        total_tables=len(request.tables),
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    job_id = job.id
    source_config = ConnectionConfig(**request.source.model_dump())
    target_config = ConnectionConfig(**request.target.model_dump())

    def worker():
        worker_db = SessionLocal()
        try:
            run_migration(
                db=worker_db,
                job_id=job_id,
                source=source_config,
                target=target_config,
                source_schema=request.source_schema,
                target_schema=request.target_schema,
                tables=request.tables,
                batch_size=request.batch_size,
                max_workers=request.max_workers,
            )
        finally:
            worker_db.close()

    background_tasks.add_task(worker)

    return {
        "job_id": job_id,
        "status": "QUEUED",
        "tables": request.tables,
        "batch_size": request.batch_size,
        "max_workers": request.max_workers,
        "message": "Migration started in background.",
    }
