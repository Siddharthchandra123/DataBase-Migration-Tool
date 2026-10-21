from app.discovery.dependencies import ForeignKey, topological_sort


def test_parent_is_before_child():
    tables = ["ORDERS", "CUSTOMERS"]

    fks = [
        ForeignKey(
            schema="APP",
            table="ORDERS",
            column="CUSTOMER_ID",
            referenced_schema="APP",
            referenced_table="CUSTOMERS",
            referenced_column="ID",
        )
    ]

    ordered = topological_sort(tables, fks)

    assert ordered.index("CUSTOMERS") < ordered.index("ORDERS")
