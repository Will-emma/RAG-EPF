import uuid
from datetime import datetime

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: uuid.UUID
    filename: str
    course_name: str | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True