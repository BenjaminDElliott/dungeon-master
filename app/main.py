"""FastAPI application entry point for Dungeon Master.

Framework decision: FastAPI was chosen over Flask because:
- Native WebSocket support for real-time LLM streaming to the browser
- Pydantic-based request/response validation built-in
- Automatic OpenAPI docs at /docs
- Async-first design matches the LLM API usage pattern
- Better type inference for code generation tools (LSP, IDEs)

All these align with the tech stack already confirmed in the epic.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.logging_setup import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown hooks."""
    settings = get_settings()
    setup_logging(level="DEBUG" if settings.debug else "INFO")
    logger.info("Dungeon Master starting up (version %s)", app.version)
    yield
    logger.info("Dungeon Master shutting down")


app = FastAPI(
    title=get_settings().app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Hello world health check."""
    return {"message": "Welcome to Dungeon Master", "status": "running"}


@app.get("/health")
async def health():
    """Health check endpoint for monitoring."""
    return {"status": "ok"}


@app.get("/api/v1/status")
async def api_status():
    """API version status."""
    return {
        "api": "v1",
        "status": "active",
        "version": "0.1.0",
    }
