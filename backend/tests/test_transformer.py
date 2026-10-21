from app.migration.transformer import DataTransformer


def test_memoryview_is_converted():
    row = {"id": 1, "payload": memoryview(b"abc")}
    result = DataTransformer().transform_row(row)
    assert result["payload"] == b"abc"
