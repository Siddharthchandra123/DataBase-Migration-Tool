from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ConnectionConfig:
    engine: str
    host: str
    port: int
    database: str
    username: str
    password: str


class DatabaseConnector(ABC):

    def __init__(self, config: ConnectionConfig):
        self.config = config

    @abstractmethod
    def connect(self):
        ...

    @abstractmethod
    def close(self):
        ...

    @abstractmethod
    def test_connection(self) -> bool:
        ...

    @abstractmethod
    def get_schemas(self) -> list[str]:
        ...

    @abstractmethod
    def get_tables(self, schema: str) -> list[str]:
        ...

    @abstractmethod
    def get_columns(self, schema: str, table: str) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    def extract_rows(self, schema: str, table: str, batch_size: int = 1000):
        ...
