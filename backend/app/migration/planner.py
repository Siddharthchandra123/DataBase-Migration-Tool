from dataclasses import dataclass


@dataclass(frozen=True)
class MigrationTaskPlan:
    source_schema: str
    source_table: str
    target_schema: str
    target_table: str


def build_plan(
    tables: list[str],
    source_schema: str,
    target_schema: str | None = None,
) -> list[MigrationTaskPlan]:
    target_schema = target_schema or source_schema

    return [
        MigrationTaskPlan(
            source_schema=source_schema,
            source_table=table,
            target_schema=target_schema,
            target_table=table,
        )
        for table in tables
    ]
