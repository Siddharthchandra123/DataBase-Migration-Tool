from typing import Any

from app.connectors.base import ConnectionConfig, DatabaseConnector
from app.connectors.db2_catalog import DB2CatalogMixin


class DB2Connector(DB2CatalogMixin, DatabaseConnector):

    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        self.connection = None

    def connect(self):
        import ibm_db

        conn_str = (
            f"DATABASE={self.config.database};"
            f"HOSTNAME={self.config.host};"
            f"PORT={self.config.port};"
            f"PROTOCOL=TCPIP;"
            f"UID={self.config.username};"
            f"PWD={self.config.password};"
        )
        self.connection = ibm_db.connect(conn_str, "", "")

    def close(self):
        if self.connection:
            import ibm_db
            ibm_db.close(self.connection)
            self.connection = None

    def test_connection(self) -> bool:
        try:
            self.connect()
            return True
        except Exception:
            return False
        finally:
            self.close()

    def get_schemas(self) -> list[str]:
        self.connect()
        try:
            import ibm_db
            stmt = ibm_db.exec_immediate(
                self.connection,
                "SELECT DISTINCT CREATOR FROM SYSCAT.TABLES "
                "WHERE TYPE='T' ORDER BY CREATOR"
            )
            result = []
            row = ibm_db.fetch_assoc(stmt)
            while row:
                result.append(row["CREATOR"])
                row = ibm_db.fetch_assoc(stmt)
            return result
        finally:
            self.close()

    def get_tables(self, schema: str) -> list[str]:
        self.connect()
        try:
            import ibm_db
            stmt = ibm_db.prepare(
                self.connection,
                "SELECT TABNAME FROM SYSCAT.TABLES "
                "WHERE CREATOR=? AND TYPE='T' ORDER BY TABNAME"
            )
            ibm_db.bind_param(stmt, 1, schema)
            ibm_db.execute(stmt)

            result = []
            row = ibm_db.fetch_assoc(stmt)
            while row:
                result.append(row["TABNAME"])
                row = ibm_db.fetch_assoc(stmt)
            return result
        finally:
            self.close()

    def get_columns(self, schema: str, table: str) -> list[dict[str, Any]]:
        self.connect()
        try:
            import ibm_db
            stmt = ibm_db.prepare(
                self.connection,
                "SELECT COLNAME,TYPENAME,NULLS,COLNO,LENGTH,SCALE "
                "FROM SYSCAT.COLUMNS WHERE TABSCHEMA=? AND TABNAME=? "
                "ORDER BY COLNO"
            )
            ibm_db.bind_param(stmt, 1, schema)
            ibm_db.bind_param(stmt, 2, table)
            ibm_db.execute(stmt)

            result = []
            row = ibm_db.fetch_assoc(stmt)
            while row:
                result.append({
                    "column_name": row["COLNAME"],
                    "data_type": row["TYPENAME"],
                    "is_nullable": row["NULLS"],
                    "ordinal_position": row["COLNO"],
                    "length": row["LENGTH"],
                    "scale": row["SCALE"],
                })
                row = ibm_db.fetch_assoc(stmt)
            return result
        finally:
            self.close()

    def extract_rows(self, schema: str, table: str, batch_size: int = 1000):
        import ibm_db

        self.connect()

        try:
            sql = f'SELECT * FROM "{schema}"."{table}" WITH UR'
            stmt = ibm_db.exec_immediate(self.connection, sql)

            while True:
                rows = []
                for _ in range(batch_size):
                    row = ibm_db.fetch_assoc(stmt)
                    if not row:
                        break
                    rows.append({str(k): v for k, v in row.items()})

                if not rows:
                    break

                yield rows
        finally:
            self.close()
