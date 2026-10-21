from app.migration.planner import build_plan


def test_build_plan():
    plan = build_plan(
        ["CUSTOMERS", "ORDERS"],
        source_schema="APP",
        target_schema="PUBLIC",
    )

    assert len(plan) == 2
    assert plan[0].source_table == "CUSTOMERS"
    assert plan[0].target_schema == "PUBLIC"
