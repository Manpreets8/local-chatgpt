import datetime

from pydantic import BaseModel, ConfigDict

from app.models.document import DocumentStatus


class DocumentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    content_type: str
    file_size_bytes: int
    status: DocumentStatus
    chunk_count: int
    error_message: str | None = None
    created_at: datetime.datetime


class DocumentDetail(DocumentSummary):
    pass
