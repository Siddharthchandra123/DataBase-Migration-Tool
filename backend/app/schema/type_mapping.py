from dataclasses import dataclass


@dataclass(frozen=True)
class TargetType:
    name: str
    length: int | None = None
    precision: int | None = None
    scale: int | None = None


DB2_TO_POSTGRES = {
    "SMALLINT": "SMALLINT",
    "INTEGER": "INTEGER",
    "INT": "INTEGER",
    "BIGINT": "BIGINT",
    "DECIMAL": "NUMERIC",
    "NUMERIC": "NUMERIC",
    "REAL": "REAL",
    "DOUBLE": "DOUBLE PRECISION",
    "FLOAT": "DOUBLE PRECISION",
    "CHAR": "CHAR",
    "VARCHAR": "VARCHAR",
    "LONG VARCHAR": "TEXT",
    "CLOB": "TEXT",
    "BLOB": "BYTEA",
    "DATE": "DATE",
    "TIME": "TIME",
    "TIMESTAMP": "TIMESTAMP",
    "BOOLEAN": "BOOLEAN",
    "XML": "XML",
}


def map_db2_type(
    source_type: str,
    length: int | None = None,
    precision: int | None = None,
    scale: int | None = None,
) -> TargetType:
    normalized = source_type.strip().upper()
    target = DB2_TO_POSTGRES.get(normalized)

    if not target:
        raise ValueError(f"Unsupported DB2 data type: {source_type}")

    if target in {"CHAR", "VARCHAR"} and length:
        return TargetType(target, length=length)

    if target == "NUMERIC" and precision:
        return TargetType(
            target,
            precision=precision,
            scale=scale or 0,
        )

    return TargetType(target)
