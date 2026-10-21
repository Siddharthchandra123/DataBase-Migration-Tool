from app.migration.constraints import (
    generate_foreign_key_ddl,
    generate_index_ddl,
    generate_primary_key_ddl,
    group_index_columns,
)


def test_pk_ddl():
    ddl = generate_primary_key_ddl(
        "public",
        "customers",
        "customers_pk",
        ["id"],
    )
    assert "PRIMARY KEY" in ddl


def test_fk_ddl():
    ddl = generate_foreign_key_ddl(
        "public",
        "orders",
        "orders_customer_fk",
        ["customer_id"],
        "public",
        "customers",
        ["id"],
    )
    assert "FOREIGN KEY" in ddl
    assert "REFERENCES" in ddl


def test_index_grouping():
    indexes = group_index_columns([
        {"index_name": "idx_orders", "unique": False, "column_name": "a", "position": 1},
        {"index_name": "idx_orders", "unique": False, "column_name": "b", "position": 2},
    ])
    assert indexes[0]["columns"] == ["a", "b"]
