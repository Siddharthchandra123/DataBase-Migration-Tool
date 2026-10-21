from app.schema.models import TableMetadata
from app.schema.type_mapping import map_db2_type


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def generate_postgres_ddl(table: TableMetadata) -> str:
    definitions = []

    for column in sorted(table.columns, key=lambda c: c.ordinal_position):
        target = map_db2_type(
            column.source_type,
            length=column.length,
            precision=column.precision,
            scale=column.scale,
        )

        if target.length:
            sql_type = f"{target.name}({target.length})"
        elif target.precision:
            sql_type = f"{target.name}({target.precision},{target.scale})"
        else:
            sql_type = target.name

        nullable = "" if column.nullable else " NOT NULL"
        definitions.append(
            f"    {quote_identifier(column.name)} {sql_type}{nullable}"
        )

    return (
        f"CREATE TABLE {quote_identifier(table.schema_name)}."
        f"{quote_identifier(table.table_name)} (\n"
        + ",\n".join(definitions)
        + "\n);"
    )
