import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()

DATABASE = os.getenv("DATABASE_URL", "sqlite:///./users.db")

class Base(DeclarativeBase):
    pass

engine = create_engine (DATABASE,  connect_args={"check_same_thread": False} if "sqlite" in DATABASE
else{})
                        
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit = False
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
