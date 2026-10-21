from app.schema.ddl import quote_identifier
from app.schema.type_mapping import map_db2_type


def build_ddl_from_source(
    source_schema: str,
    source_table: str,
    columns: list[dict],
    target_schema: str,
) -> str:
    definitions = []

    for column in columns:
        target = map_db2_type(
            source_type=column["data_type"],
            length=column.get("length"),
            precision=column.get("precision"),
            scale=column.get("scale"),
        )

        if target.length:
            sql_type = f"{target.name}({target.length})"
        elif target.precision:
            sql_type = f"{target.name}({target.precision},{target.scale})"
        else:
            sql_type = target.name

        nullable = ""
        if str(column.get("is_nullable", "Y")).upper() in {"N", "NO", "FALSE"}:
            nullable = " NOT NULL"

        definitions.append(
            f'    {quote_identifier(column["column_name"])} '
            f"{sql_type}{nullable}"
        )

    return (
        f'CREATE TABLE IF NOT EXISTS '
        f'{quote_identifier(target_schema)}.{quote_identifier(source_table)} (\n'
        + ",\n".join(definitions)
        + "\n);"
    )
