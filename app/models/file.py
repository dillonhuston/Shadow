from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.db import Base
from datetime import datetime
from typing import Optional

class File(Base):
    __tablename__ = 'files'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey('user.id'), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    filepath: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)