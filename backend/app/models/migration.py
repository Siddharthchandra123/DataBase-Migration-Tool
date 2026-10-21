from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class MigrationJob(Base):
    __tablename__ = "migration_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    source_engine: Mapped[str] = mapped_column(String(50))
    target_engine: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="CREATED")
    total_tables: Mapped[int] = mapped_column(Integer, default=0)
    completed_tables: Mapped[int] = mapped_column(Integer, default=0)
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    migrated_rows: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MigrationTask(Base):
    __tablename__ = "migration_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(Integer, index=True)
    source_schema: Mapped[str] = mapped_column(String(255))
    source_table: Mapped[str] = mapped_column(String(255))
    target_schema: Mapped[str] = mapped_column(String(255))
    target_table: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="PENDING")
    rows_processed: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class MigrationCheckpoint(Base):
    __tablename__ = "migration_checkpoints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(Integer, index=True)
    table_name: Mapped[str] = mapped_column(String(255))
    batches_completed: Mapped[int] = mapped_column(Integer, default=0)
    rows_migrated: Mapped[int] = mapped_column(Integer, default=0)
    last_source_key: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
