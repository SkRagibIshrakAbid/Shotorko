from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NoteCreate(BaseModel):
    content: str
    is_anonymous: bool = True


class NoteOut(BaseModel):
    id: str
    crime_id: str
    content: str
    is_anonymous: bool
    author_id: Optional[str] = None
    author_name: Optional[str] = None
    upvotes: int = 0
    downvotes: int = 0
    created_at: datetime
