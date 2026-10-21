from sqlalchemy import text
from sqlalchemy.orm import Session

from app.connectors.base import ConnectionConfig
from app.connectors.factory import create_connector
from app.core.database import SessionLocal
from app.migration.ddl_live import build_ddl_from_source
from app.migration.executor import MigrationExecutor
from app.migration.loader import PostgreSQLLoader
from app.migration.parallel import WorkerResult, run_parallel
from app.migration.transformer import DataTransformer
from app.models.migration import MigrationJob, MigrationTask
from app.validation.service import ValidationService


def count_postgres_rows(loader, schema: str, table: str) -> int:
    with loader.engine.connect() as conn:
        result = conn.execute(
            text(f'SELECT COUNT(*) FROM "{schema}"."{table}"')
        )
        return int(result.scalar_one())


def run_single_table(
    job_id: int,
    source: ConnectionConfig,
    target: ConnectionConfig,
    source_schema: str,
    target_schema: str,
    table_name: str,
    batch_size: int,
) -> WorkerResult:
    db = SessionLocal()
    source_connector = create_connector(source)

    target_loader = PostgreSQLLoader(
        host=target.host,
        port=target.port,
        database=target.database,
        username=target.username,
        password=target.password,
    )

    try:
        task = MigrationTask(
            job_id=job_id,
            source_schema=source_schema,
            source_table=table_name,
            target_schema=target_schema,
            target_table=table_name,
            status="RUNNING",
        )
        db.add(task)
        db.commit()

        columns = source_connector.get_columns(source_schema, table_name)

        ddl = build_ddl_from_source(
            source_schema,
            table_name,
            columns,
            target_schema,
        )

        executor = MigrationExecutor(
            source_connector=source_connector,
            target_loader=target_loader,
            transformer=DataTransformer(),
        )

        result = executor.migrate_table(
            source_schema=source_schema,
            source_table=table_name,
            target_schema=target_schema,
            target_table=table_name,
            ddl=ddl,
            batch_size=batch_size,
        )

        if result.status != "COMPLETED":
            raise RuntimeError(result.error or "Migration failed")

        target_count = count_postgres_rows(
            target_loader,
            target_schema,
            table_name,
        )

        validation = ValidationService().validate_row_counts(
            result.rows_migrated,
            target_count,
        )

        task.rows_processed = result.rows_migrated
        task.status = "COMPLETED" if validation.passed else "VALIDATION_FAILED"

        if not validation.passed:
            task.error_message = validation.message

        db.commit()

        return WorkerResult(
            table=table_name,
            success=validation.passed,
            rows=result.rows_migrated,
            error=None if validation.passed else validation.message,
        )

    except Exception as exc:
        db.rollback()

        task = MigrationTask(
            job_id=job_id,
            source_schema=source_schema,
            source_table=table_name,
            target_schema=target_schema,
            target_table=table_name,
            status="FAILED",
            error_message=str(exc),
        )
        db.add(task)
        db.commit()

        return WorkerResult(
            table=table_name,
            success=False,
            error=str(exc),
        )

    finally:
        source_connector.close()
        target_loader.close()
        db.close()


def run_migration(
    db: Session,
    job_id: int,
    source: ConnectionConfig,
    target: ConnectionConfig,
    source_schema: str,
    target_schema: str,
    tables: list[str],
    batch_size: int = 5000,
    max_workers: int = 1,
):
    job = db.get(MigrationJob, job_id)

    if not job:
        raise ValueError(f"Migration job {job_id} not found")

    job.status = "RUNNING"
    job.total_tables = len(tables)
    job.completed_tables = 0
    job.migrated_rows = 0
    job.error_count = 0
    db.commit()

    try:
        def worker(table_name: str):
            return run_single_table(
                job_id=job_id,
                source=source,
                target=target,
                source_schema=source_schema,
                target_schema=target_schema,
                table_name=table_name,
                batch_size=batch_size,
            )

        results = run_parallel(
            tables,
            worker,
            max_workers=max_workers,
        )

        job.completed_tables = sum(1 for r in results if r.success)
        job.migrated_rows = sum(r.rows for r in results)
        job.error_count = sum(1 for r in results if not r.success)

        if job.error_count:
            job.status = "COMPLETED_WITH_ERRORS"
            errors = [
                f"{r.table}: {r.error}"
                for r in results
                if not r.success and r.error
            ]
            job.error_message = "; ".join(errors[:10])
        else:
            job.status = "COMPLETED"

        db.commit()

    except Exception as exc:
        job.status = "FAILED"
        job.error_message = str(exc)
        db.commit()
        raise
