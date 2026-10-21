from typing import Any

from sqlalchemy import create_engine, text


class PostgreSQLLoader:
    def __init__(self, host: str, port: int, database: str, username: str, password: str):
        self.engine = create_engine(
            f"postgresql+psycopg://{username}:{password}"
            f"@{host}:{port}/{database}",
            pool_pre_ping=True,
        )

    def close(self):
        self.engine.dispose()

    def ensure_table(self, schema: str, table: str, ddl: str):
        with self.engine.begin() as conn:
            conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
            conn.execute(text(ddl))

    def insert_batch(
        self,
        schema: str,
        table: str,
        rows: list[dict[str, Any]],
    ) -> int:
        if not rows:
            return 0

        columns = list(rows[0].keys())
        quoted_columns = ", ".join(
            '"' + column.replace('"', '""') + '"' for column in columns
        )
        parameters = ", ".join(f":p{i}" for i in range(len(columns)))

        statement = text(
            f'INSERT INTO "{schema}"."{table}" '
            f"({quoted_columns}) VALUES ({parameters})"
        )

        payload = [
            {f"p{i}": row[column] for i, column in enumerate(columns)}
            for row in rows
        ]

        with self.engine.begin() as conn:
            conn.execute(statement, payload)

        return len(rows)

    def copy_batch(
        self,
        schema: str,
        table: str,
        rows: list[dict[str, Any]],
    ) -> int:
        """High-throughput PostgreSQL COPY path.

        Uses psycopg's COPY interface through the SQLAlchemy raw connection.
        The fallback INSERT path remains available for unusual values.
        """
        if not rows:
            return 0

        raw = self.engine.raw_connection()

        try:
            cursor = raw.cursor()
            columns = list(rows[0].keys())

            quoted_columns = ", ".join(
                '"' + column.replace('"', '""') + '"'
                for column in columns
            )

            copy_sql = (
                f'COPY "{schema}"."{table}" ({quoted_columns}) '
                f"FROM STDIN WITH (FORMAT CSV, NULL '\\N')"
            )

            with cursor.copy(copy_sql) as copy:
                for row in rows:
                    values = [
                        self._csv_value(row.get(column))
                        for column in columns
                    ]
                    copy.write_row(values)

            raw.commit()
            return len(rows)

        except Exception:
            raw.rollback()
            raise
        finally:
            raw.close()

    @staticmethod
    def _csv_value(value):
        if value is None:
            return "\\N"
        if isinstance(value, bytes):
            return value
        return value
