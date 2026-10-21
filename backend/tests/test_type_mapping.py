from app.schema.type_mapping import map_db2_type


def test_varchar_mapping():
    result = map_db2_type("VARCHAR", length=120)
    assert result.name == "VARCHAR"
    assert result.length == 120


def test_decimal_mapping():
    result = map_db2_type("DECIMAL", precision=18, scale=4)
    assert result.name == "NUMERIC"
    assert result.precision == 18
    assert result.scale == 4


def test_clob_mapping():
    assert map_db2_type("CLOB").name == "TEXT"
