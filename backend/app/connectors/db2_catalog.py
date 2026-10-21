from typing import Any


class DB2CatalogMixin:
    """Catalog helpers shared by the DB2 connector."""

    def get_primary_keys(self, schema: str, table: str) -> list[dict[str, Any]]:
        self.connect()
        try:
            import ibm_db

            stmt = ibm_db.prepare(
                self.connection,
                """
                SELECT KC.COLNAME, KC.COLSEQ, TC.CONSTNAME
                FROM SYSCAT.KEYCOLUSE KC
                JOIN SYSCAT.TABCONST TC
                  ON TC.TABSCHEMA = KC.TABSCHEMA
                 AND TC.TABNAME = KC.TABNAME
                 AND TC.CONSTNAME = KC.CONSTNAME
                WHERE KC.TABSCHEMA = ?
                  AND KC.TABNAME = ?
                  AND TC.TYPE = 'P'
                ORDER BY KC.COLSEQ
                """,
            )
            ibm_db.bind_param(stmt, 1, schema)
            ibm_db.bind_param(stmt, 2, table)
            ibm_db.execute(stmt)

            result = []
            row = ibm_db.fetch_assoc(stmt)
            while row:
                result.append({
                    "column_name": row["COLNAME"],
                    "position": row["COLSEQ"],
                    "constraint_name": row["CONSTNAME"],
                })
                row = ibm_db.fetch_assoc(stmt)

            return result
        finally:
            self.close()

    def get_foreign_keys(self, schema: str, table: str) -> list[dict[str, Any]]:
        self.connect()
        try:
            import ibm_db

            stmt = ibm_db.prepare(
                self.connection,
                """
                SELECT
                    R.CONSTNAME,
                    R.TABSCHEMA,
                    R.TABNAME,
                    R.REFTABSCHEMA,
                    R.REFTABNAME,
                    K.COLNAME,
                    RK.COLNAME AS REFCOLNAME,
                    K.COLSEQ
                FROM SYSCAT.REFERENCES R
                JOIN SYSCAT.KEYCOLUSE K
                  ON K.TABSCHEMA = R.TABSCHEMA
                 AND K.TABNAME = R.TABNAME
                 AND K.CONSTNAME = R.CONSTNAME
                JOIN SYSCAT.KEYCOLUSE RK
                  ON RK.TABSCHEMA = R.REFTABSCHEMA
                 AND RK.TABNAME = R.REFTABNAME
                 AND RK.CONSTNAME = R.REFKEYNAME
                 AND RK.COLSEQ = K.COLSEQ
                WHERE R.TABSCHEMA = ?
                  AND R.TABNAME = ?
                ORDER BY R.CONSTNAME, K.COLSEQ
                """,
            )
            ibm_db.bind_param(stmt, 1, schema)
            ibm_db.bind_param(stmt, 2, table)
            ibm_db.execute(stmt)

            result = []
            row = ibm_db.fetch_assoc(stmt)
            while row:
                result.append({
                    "constraint_name": row["CONSTNAME"],
                    "schema": row["TABSCHEMA"],
                    "table": row["TABNAME"],
                    "column_name": row["COLNAME"],
                    "referenced_schema": row["REFTABSCHEMA"],
                    "referenced_table": row["REFTABNAME"],
                    "referenced_column": row["REFCOLNAME"],
                    "position": row["COLSEQ"],
                })
                row = ibm_db.fetch_assoc(stmt)

            return result
        finally:
            self.close()

    def get_indexes(self, schema: str, table: str) -> list[dict[str, Any]]:
        self.connect()
        try:
            import ibm_db

            stmt = ibm_db.prepare(
                self.connection,
                """
                SELECT I.INDNAME, I.UNIQUERULE, IC.COLNAME, IC.COLSEQ
                FROM SYSCAT.INDEXES I
                JOIN SYSCAT.INDEXCOLUSE IC
                  ON IC.INDSCHEMA = I.INDSCHEMA
                 AND IC.INDNAME = I.INDNAME
                WHERE I.TABSCHEMA = ?
                  AND I.TABNAME = ?
                ORDER BY I.INDNAME, IC.COLSEQ
                """,
            )
            ibm_db.bind_param(stmt, 1, schema)
            ibm_db.bind_param(stmt, 2, table)
            ibm_db.execute(stmt)

            result = []
            row = ibm_db.fetch_assoc(stmt)
            while row:
                result.append({
                    "index_name": row["INDNAME"],
                    "unique": row["UNIQUERULE"] == "U",
                    "column_name": row["COLNAME"],
                    "position": row["COLSEQ"],
                })
                row = ibm_db.fetch_assoc(stmt)

            return result
        finally:
            self.close()
