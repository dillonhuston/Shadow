from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions.exceptions import ServiceError # changed to include correct directory.

async def service_exception_handler(request: Request, exc: ServiceError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."},
    )