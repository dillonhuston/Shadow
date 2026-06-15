from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from app.models.db import Base
from datetime import datetime

class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('user.id'), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=True)  
    filepath = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


   