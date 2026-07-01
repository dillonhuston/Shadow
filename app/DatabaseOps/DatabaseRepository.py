import uuid

from typing import Optional, List, Sequence

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.file import File as FileModel
class DatabaseOps():
    
    async def GetUserByusername(self, db: AsyncSession, user: str)-> Optional[User]:
        result = await db.execute(select(User).where(User.username == user))
        return result.scalar_one_or_none()
    
    async def GetUserFileByUserid(self, db: AsyncSession, user_id: str)->Sequence[FileModel]:
        result =  await db.execute(select(FileModel).where(FileModel.user_id == user_id))
        return result.scalars().all()
    
    async def GetFileEntry(self, db: AsyncSession, user_id: str, file_id: int)->Optional[FileModel]:
        result = await db.execute(select(FileModel).where(
            FileModel.user_id == user_id, #changed this to user_id instead of file_id
            FileModel.id == file_id, # got these both mixed up
            ))
        return result.scalar_one_or_none()
        
    async def remove_file(self, db: AsyncSession, user_id: str, file_id: int)-> bool:
        file_entry = await self.GetFileEntry(
            db,
            user_id,
            file_id
        )
        if file_entry:
            await db.delete(file_entry)
            await db.commit()
            return True
        return False


    async def add(self, db: AsyncSession, user: User)-> User:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    

    async def add_file(self, db: AsyncSession, file: FileModel)-> FileModel:
        db.add(file)
        await db.commit()
        await db.refresh(file)
        return file    