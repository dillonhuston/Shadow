from app.models.file import File
from app.models.user import User
from app.models.db import Base, engine

Base.metadata.create_all(bind=engine)
print("created_tables_successfully")

