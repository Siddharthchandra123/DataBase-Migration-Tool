from typing import Any


class DataTransformer:
    """Normalizes values before target insertion.

    The first implementation deliberately stays conservative:
    values are preserved whenever possible and only obvious binary
    memoryview values are converted to bytes.
    """

    @staticmethod
    def transform_row(row: dict[str, Any]) -> dict[str, Any]:
        transformed = {}

        for key, value in row.items():
            if isinstance(value, memoryview):
                transformed[key] = value.tobytes()
            else:
                transformed[key] = value

        return transformed

    def transform_batch(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [self.transform_row(row) for row in rows]
