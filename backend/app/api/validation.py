from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.validation.checksum import batch_checksum
from app.validation.service import ValidationService

router = APIRouter()


class RowCountRequest(BaseModel):
    source_rows: int = Field(ge=0)
    target_rows: int = Field(ge=0)


class ChecksumRequest(BaseModel):
    rows: list[dict]


@router.post("/row-count")
def validate_row_count(request: RowCountRequest):
    return ValidationService().validate_row_counts(
        request.source_rows,
        request.target_rows,
    )


@router.post("/checksum")
def calculate_checksum(request: ChecksumRequest):
    return {
        "algorithm": "SHA-256",
        "checksum": batch_checksum(request.rows),
        "row_count": len(request.rows),
    }
