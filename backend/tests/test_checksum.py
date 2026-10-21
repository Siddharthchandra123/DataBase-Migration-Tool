from app.validation.checksum import batch_checksum, row_checksum


def test_row_checksum_is_deterministic():
    row_a = {"id": 1, "name": "Alice"}
    row_b = {"name": "Alice", "id": 1}

    assert row_checksum(row_a) == row_checksum(row_b)


def test_batch_checksum_changes_when_data_changes():
    first = batch_checksum([{"id": 1}])
    second = batch_checksum([{"id": 2}])

    assert first != second
