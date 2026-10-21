from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Callable, Iterable


@dataclass
class WorkerResult:
    table: str
    success: bool
    rows: int = 0
    error: str | None = None


def run_parallel(
    tables: Iterable[str],
    worker: Callable[[str], WorkerResult],
    max_workers: int = 4,
) -> list[WorkerResult]:
    tables = list(tables)
    if not tables:
        return []

    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(worker, table): table
            for table in tables
        }

        for future in as_completed(futures):
            table = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                results.append(
                    WorkerResult(
                        table=table,
                        success=False,
                        error=str(exc),
                    )
                )

    return results
