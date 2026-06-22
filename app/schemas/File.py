from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class File(BaseModel):
    id: Optional[int] = None
    filename: str
    filepath: str
    original_filename: Optional[str] = None
    user_id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  