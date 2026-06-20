import uuid

from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.User import UserSignup

class DatabaseOps():
    
    def GetUserByusername(self, db: Session, user: str):
        return db.query(User).filter(User.username == user).first()

    def add(self, db: Session, user: User):
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
        