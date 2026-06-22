import uuid

from sqlalchemy.orm import Session
from app.models.user import User
from app.models.file import File as FileModel
class DatabaseOps():
    
    def GetUserByusername(self, db: Session, user: str):
        return db.query(User).filter(User.username == user).first()
    
    def GetUserFileByUserid(self, db: Session, user_id: str):
        return db.query(FileModel).filter(FileModel.user_id == user_id).all()
    
    def GetFileEntry(self, db: Session, user_id: str, file_id: int):
        return db.query(FileModel).filter_by(
            id=file_id,
            user_id = user_id
        ).first()
        
    def remove_file(self, db: Session, user_id: str, file_id: int):
        file_entry = self.GetFileEntry(
            db,
            user_id,
            file_id
        )
        return db.delete(file_entry), db.commit()


    def add(self, db: Session, user: User):
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    

    def add_file(self, db: Session, file: FileModel):
        db.add(file)
        db.commit()
        db.refresh(file)
        return file    