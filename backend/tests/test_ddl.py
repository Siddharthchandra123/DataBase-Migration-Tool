from app.schema.ddl import generate_postgres_ddl
from app.schema.models import ColumnMetadata, TableMetadata


def test_generate_ddl():
    table = TableMetadata(
        schema_name="APP",
        table_name="CUSTOMERS",
        columns=[
            ColumnMetadata(
                name="ID",
                source_type="BIGINT",
                nullable=False,
                ordinal_position=1,
            ),
            ColumnMetadata(
                name="NAME",
                source_type="VARCHAR",
                length=100,
                nullable=True,
                ordinal_position=2,
            ),
        ],
    )

    ddl = generate_postgres_ddl(table)

    assert 'CREATE TABLE "APP"."CUSTOMERS"' in ddl
    assert '"ID" BIGINT NOT NULL' in ddl
    assert '"NAME" VARCHAR(100)' in ddl
