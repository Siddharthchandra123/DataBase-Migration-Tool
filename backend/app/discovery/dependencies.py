from dataclasses import dataclass


@dataclass(frozen=True)
class ForeignKey:
    schema: str
    table: str
    column: str
    referenced_schema: str
    referenced_table: str
    referenced_column: str


def topological_sort(
    tables: list[str],
    foreign_keys: list[ForeignKey],
) -> list[str]:
    table_set = set(tables)
    dependencies = {table: set() for table in tables}

    for fk in foreign_keys:
        if (
            fk.table in table_set
            and fk.referenced_table in table_set
            and fk.table != fk.referenced_table
        ):
            dependencies[fk.table].add(fk.referenced_table)

    ordered = []

    while dependencies:
        ready = sorted(
            table
            for table, deps in dependencies.items()
            if not deps
        )

        if not ready:
            # Cyclic dependencies. Keep deterministic ordering and let
            # the migration layer handle deferred constraints later.
            ordered.extend(sorted(dependencies.keys()))
            break

        ordered.extend(ready)

        for table in ready:
            dependencies.pop(table)

        for deps in dependencies.values():
            deps.difference_update(ready)

    return ordered
