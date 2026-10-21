from dataclasses import dataclass


@dataclass
class TableValidation:
    source_rows: int
    target_rows: int
    passed: bool
    message: str


class ValidationService:
    def validate_row_counts(
        self,
        source_count: int,
        target_count: int,
    ) -> TableValidation:
        passed = source_count == target_count

        if passed:
            message = "Row counts match."
        else:
            message = (
                f"Row count mismatch: source={source_count}, "
                f"target={target_count}"
            )

        return TableValidation(
            source_rows=source_count,
            target_rows=target_count,
            passed=passed,
            message=message,
        )
