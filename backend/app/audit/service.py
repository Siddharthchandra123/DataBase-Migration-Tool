from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, Session

from app.core.database import Base


class MigrationEvent(Base):
    __tablename__ = "migration_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(Integer, index=True)
    event_type: Mapped[str] = mapped_column(String(80))
    table_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


def record_event(
    db: Session,
    job_id: int,
    event_type: str,
    message: str,
    table_name: str | None = None,
):
    event = MigrationEvent(
        job_id=job_id,
        event_type=event_type,
        table_name=table_name,
        message=message,
    )
    db.add(event)
    db.commit()
    return event
