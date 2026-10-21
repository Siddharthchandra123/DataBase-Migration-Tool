from app.connectors.base import ConnectionConfig, DatabaseConnector
from app.connectors.db2 import DB2Connector
from app.connectors.postgres import PostgreSQLConnector


def create_connector(config: ConnectionConfig) -> DatabaseConnector:
    engine = config.engine.lower()

    if engine in {"postgres", "postgresql"}:
        return PostgreSQLConnector(config)

    if engine == "db2":
        return DB2Connector(config)

    raise ValueError(f"Unsupported database engine: {config.engine}")
