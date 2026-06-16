import uuid
import os

from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.db import Base
from datetime import datetime


class User(Base):
    __tablename__ = 'user' 
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    key: Mapped[str] = mapped_column(String(32), nullable=False)  
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def get_key(self) -> str:
        """Return the user's encryption key."""
        return self.key
    
    def set_key(self, new_key: str) -> None:
        """Set a new encryption key for the user."""
        self.key = new_key