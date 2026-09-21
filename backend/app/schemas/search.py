import uuid

from pydantic import BaseModel


class ChunkResult(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    filename: str
    course_name: str | None
    page_number: int | None
    content: str
    score: float

    class Config:
        from_attributes = True