from collections import defaultdict


def generate_primary_key_ddl(
    schema: str,
    table: str,
    constraint_name: str,
    columns: list[str],
) -> str:
    quoted = ", ".join(f'"{c.replace(chr(34), chr(34) * 2)}"' for c in columns)
    return (
        f'ALTER TABLE "{schema}"."{table}" '
        f'ADD CONSTRAINT "{constraint_name}" PRIMARY KEY ({quoted});'
    )


def generate_foreign_key_ddl(
    schema: str,
    table: str,
    constraint_name: str,
    columns: list[str],
    referenced_schema: str,
    referenced_table: str,
    referenced_columns: list[str],
) -> str:
    source_cols = ", ".join(
        f'"{c.replace(chr(34), chr(34) * 2)}"' for c in columns
    )
    target_cols = ", ".join(
        f'"{c.replace(chr(34), chr(34) * 2)}"' for c in referenced_columns
    )

    return (
        f'ALTER TABLE "{schema}"."{table}" '
        f'ADD CONSTRAINT "{constraint_name}" FOREIGN KEY ({source_cols}) '
        f'REFERENCES "{referenced_schema}"."{referenced_table}" '
        f'({target_cols});'
    )


def generate_index_ddl(
    schema: str,
    table: str,
    index_name: str,
    columns: list[str],
    unique: bool = False,
) -> str:
    unique_sql = "UNIQUE " if unique else ""
    quoted = ", ".join(
        f'"{c.replace(chr(34), chr(34) * 2)}"' for c in columns
    )

    return (
        f'CREATE {unique_sql}INDEX "{index_name}" '
        f'ON "{schema}"."{table}" ({quoted});'
    )


def group_index_columns(index_rows: list[dict]) -> list[dict]:
    grouped = defaultdict(list)

    for row in index_rows:
        grouped[row["index_name"]].append(row)

    result = []

    for index_name, rows in grouped.items():
        rows.sort(key=lambda r: r["position"])
        result.append({
            "index_name": index_name,
            "unique": rows[0]["unique"],
            "columns": [r["column_name"] for r in rows],
        })

    return result
