from app.validation.service import ValidationService


def test_row_count_validation_passes():
    result = ValidationService().validate_row_counts(100, 100)
    assert result.passed is True


def test_row_count_validation_fails():
    result = ValidationService().validate_row_counts(100, 99)
    assert result.passed is False
