import hashlib
import json
from typing import Any


def canonical_value(value: Any) -> str:
    if isinstance(value, bytes):
        return value.hex()
    if value is None:
        return "NULL"
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def row_checksum(row: dict[str, Any]) -> str:
    payload = [
        (key, canonical_value(row[key]))
        for key in sorted(row.keys())
    ]
    encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def batch_checksum(rows: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()

    for row in rows:
        digest.update(row_checksum(row).encode("ascii"))

    return digest.hexdigest()
