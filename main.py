
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth import router as auth_router
from app.routers.file import router as file_router
from app.routers.user import router as user_router
from app.exceptions.exceptions import ServiceError
from app.core.exception_handlers import service_exception_handler, unhandled_exception_handler

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_exception_handler(ServiceError, service_exception_handler)

app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(auth_router)
app.include_router(file_router)
app.include_router(user_router)


@app.get('/health')
def health():
    return 'ok', 200