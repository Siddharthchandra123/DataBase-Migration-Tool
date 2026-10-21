from typing import Any
from sqlalchemy import create_engine, text

from app.connectors.base import ConnectionConfig, DatabaseConnector


class PostgreSQLConnector(DatabaseConnector):

    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        self.engine = create_engine(
            f"postgresql+psycopg://{config.username}:{config.password}"
            f"@{config.host}:{config.port}/{config.database}",
            pool_pre_ping=True,
        )

    def connect(self):
        with self.engine.connect():
            pass

    def close(self):
        self.engine.dispose()

    def test_connection(self) -> bool:
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def get_schemas(self) -> list[str]:
        sql = text("""
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name NOT IN ('information_schema')
              AND schema_name NOT LIKE 'pg_%'
            ORDER BY schema_name
        """)
        with self.engine.connect() as conn:
            return [row[0] for row in conn.execute(sql)]

    def get_tables(self, schema: str) -> list[str]:
        sql = text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = :schema
              AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        with self.engine.connect() as conn:
            return [row[0] for row in conn.execute(sql, {"schema": schema})]

    def get_columns(self, schema: str, table: str) -> list[dict[str, Any]]:
        sql = text("""
            SELECT column_name, data_type, is_nullable, ordinal_position,
                   character_maximum_length, numeric_precision, numeric_scale
            FROM information_schema.columns
            WHERE table_schema = :schema AND table_name = :table
            ORDER BY ordinal_position
        """)
        with self.engine.connect() as conn:
            return [dict(row._mapping) for row in conn.execute(
                sql, {"schema": schema, "table": table}
            )]

    def extract_rows(self, schema: str, table: str, batch_size: int = 1000):
        query = text(f'SELECT * FROM "{schema}"."{table}"')
        with self.engine.connect() as conn:
            result = conn.execution_options(stream_results=True).execute(query)
            while True:
                batch = result.fetchmany(batch_size)
                if not batch:
                    break
                yield [dict(row._mapping) for row in batch]
