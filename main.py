import os
import base64
import re
from fastapi import FastAPI, APIRouter
from app.routers.auth import router as auth_router
from app.routers.file import router as file_router
#from app.routers.user import router as user_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(file_router)
#app.include_router(user_router)


@app.get('/health')
def health():
    return 'ok', 200


