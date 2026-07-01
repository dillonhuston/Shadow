from typing import cast
from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions.exceptions import ServiceError

# FIX: Whenever you implement, you should have taken into account for FastAPI's internal type 
# definitions for handlers. It requires the base 'Exception' type, so we 
# cast it to make the type checker happy.
async def service_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Cast to ServiceError so we can access specific attributes safely
    service_exc = cast(ServiceError, exc)
    
    return JSONResponse(
        status_code=service_exc.status_code,
        content={"detail": service_exc.detail},
    )

async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # NOTE: This is fine as is, since it handles generic exceptions. ---
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."},
    )