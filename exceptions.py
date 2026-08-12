from fastapi import (
    FastAPI,
    HTTPException,
    Request
)

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def register_exception_handlers(app: FastAPI):

    # ==========================================
    # HTTPException Handler
    # ==========================================

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "detail": exc.detail
            }
        )

    # ==========================================
    # Validation Error Handler
    # ==========================================

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ):
        errors = []

        for error in exc.errors():
            errors.append({
                "type": error.get("type"),
                "loc": error.get("loc"),
                "msg": error.get("msg")
            })

        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "detail": "Validation error",
                "errors": errors
            }
        )

    # ==========================================
    # General Exception Handler
    # ==========================================

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception
    ):
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "detail": "Internal server error"
            }
        )