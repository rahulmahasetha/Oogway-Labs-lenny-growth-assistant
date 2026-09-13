"""FastAPI application factory and startup."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import config, health, ingestion, messages, sessions, sources
from app.utils.errors import register_error_handlers
from app.utils.logging import get_logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: setup logging on startup."""
    setup_logging()
    logger = get_logger("app")
    logger.info("application_starting", version="1.0.0")
    yield
    logger.info("application_shutting_down")


app = FastAPI(
    title="Lenny Growth Assistant",
    description="AI-powered product management assistant grounded in Lenny's Podcast transcripts",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register error handlers
register_error_handlers(app)

# Register routers
app.include_router(health.router, tags=["Health"])
app.include_router(sessions.router, prefix="/api", tags=["Sessions"])
app.include_router(messages.router, prefix="/api", tags=["Messages"])
app.include_router(ingestion.router, prefix="/api", tags=["Ingestion"])
app.include_router(sources.router, prefix="/api", tags=["Sources"])
app.include_router(config.router, prefix="/api", tags=["Config"])
