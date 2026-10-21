from app.migration.parallel import WorkerResult, run_parallel


def test_parallel_worker():
    def worker(table):
        return WorkerResult(table=table, success=True, rows=10)

    results = run_parallel(["A", "B", "C"], worker, max_workers=2)

    assert len(results) == 3
    assert all(result.success for result in results)
