from sqlalchemy import Column, String, DateTime
from app.models.db import Base
from datetime import datetime
import uuid
import os

class User(Base):
    __tablename__ = 'user' 
    id = Column(String(36), primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    key = Column(String(32), nullable=False)  
    created_at = Column(DateTime, default=datetime.utcnow)

  