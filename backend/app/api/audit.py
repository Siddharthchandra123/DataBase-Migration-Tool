from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.service import MigrationEvent
from app.core.database import get_db

router = APIRouter()


@router.get("/{job_id}/events")
def get_events(job_id: int, db: Session = Depends(get_db)):
    events = db.scalars(
        select(MigrationEvent)
        .where(MigrationEvent.job_id == job_id)
        .order_by(MigrationEvent.created_at.asc())
    ).all()

    return {
        "job_id": job_id,
        "events": [
            {
                "id": event.id,
                "event_type": event.event_type,
                "table_name": event.table_name,
                "message": event.message,
                "created_at": event.created_at.isoformat(),
            }
            for event in events
        ],
    }
