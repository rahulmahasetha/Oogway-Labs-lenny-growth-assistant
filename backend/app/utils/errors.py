"""Centralized error handling for the FastAPI application."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.utils.logging import get_logger

logger = get_logger("errors")


class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, status_code: int = 500, detail: str | None = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


class NotFoundError(AppError):
    """Resource not found."""

    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            message=f"{resource} not found",
            status_code=404,
            detail=f"{resource} with id '{resource_id}' does not exist",
        )


class ProviderError(AppError):
    """LLM provider error."""

    def __init__(self, provider: str, detail: str):
        super().__init__(
            message=f"LLM provider '{provider}' error",
            status_code=503,
            detail=detail,
        )


class ValidationError(AppError):
    """Request validation error."""

    def __init__(self, detail: str):
        super().__init__(
            message="Validation error",
            status_code=422,
            detail=detail,
        )


def register_error_handlers(app: FastAPI) -> None:
    """Register global error handlers on the FastAPI app."""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        logger.error(
            "application_error",
            error=exc.message,
            detail=exc.detail,
            status_code=exc.status_code,
            path=str(request.url),
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "detail": exc.detail},
        )

    @app.exception_handler(SQLAlchemyError)
    async def db_error_handler(request: Request, exc: SQLAlchemyError):
        logger.error("database_error", error=str(exc), path=str(request.url))
        return JSONResponse(
            status_code=503,
            content={
                "error": "Database error",
                "detail": "A database error occurred. Please try again.",
            },
        )

    @app.exception_handler(Exception)
    async def general_error_handler(request: Request, exc: Exception):
        logger.error(
            "unhandled_error",
            error=str(exc),
            error_type=type(exc).__name__,
            path=str(request.url),
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": "An unexpected error occurred.",
            },
        )
