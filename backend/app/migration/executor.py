from dataclasses import dataclass
from typing import Callable

from app.migration.transformer import DataTransformer


@dataclass
class MigrationResult:
    table: str
    rows_migrated: int
    batches: int
    status: str
    error: str | None = None


class MigrationExecutor:
    def __init__(
        self,
        source_connector,
        target_loader,
        transformer: DataTransformer | None = None,
    ):
        self.source = source_connector
        self.target = target_loader
        self.transformer = transformer or DataTransformer()

    def migrate_table(
        self,
        source_schema: str,
        source_table: str,
        target_schema: str,
        target_table: str,
        ddl: str,
        batch_size: int = 1000,
        on_progress: Callable[[int], None] | None = None,
    ) -> MigrationResult:
        migrated = 0
        batches = 0

        try:
            self.target.ensure_table(target_schema, target_table, ddl)

            for rows in self.source.extract_rows(
                source_schema,
                source_table,
                batch_size=batch_size,
            ):
                transformed = self.transformer.transform_batch(rows)
                count = self.target.insert_batch(
                    target_schema,
                    target_table,
                    transformed,
                )
                migrated += count
                batches += 1

                if on_progress:
                    on_progress(migrated)

            return MigrationResult(
                table=source_table,
                rows_migrated=migrated,
                batches=batches,
                status="COMPLETED",
            )

        except Exception as exc:
            return MigrationResult(
                table=source_table,
                rows_migrated=migrated,
                batches=batches,
                status="FAILED",
                error=str(exc),
            )
