from dataclasses import dataclass
from datetime import datetime


@dataclass
class Checkpoint:
    job_id: int
    table_name: str
    batches_completed: int = 0
    rows_migrated: int = 0
    last_updated: datetime | None = None


class CheckpointStore:
    def __init__(self):
        self._checkpoints: dict[tuple[int, str], Checkpoint] = {}

    def get(self, job_id: int, table_name: str) -> Checkpoint | None:
        return self._checkpoints.get((job_id, table_name))

    def save(
        self,
        job_id: int,
        table_name: str,
        batches_completed: int,
        rows_migrated: int,
    ) -> Checkpoint:
        checkpoint = Checkpoint(
            job_id=job_id,
            table_name=table_name,
            batches_completed=batches_completed,
            rows_migrated=rows_migrated,
            last_updated=datetime.utcnow(),
        )
        self._checkpoints[(job_id, table_name)] = checkpoint
        return checkpoint
