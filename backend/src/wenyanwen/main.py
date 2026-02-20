"""FastAPI application factory."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_db
from .api.v1 import quiz, review


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the application."""
    # Startup
    init_db()
    yield
    # Shutdown
    pass


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="文言文实词虚词记忆工具 API",
        description="基于错误驱动和艾宾浩斯遗忘曲线的记忆辅助工具",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(quiz.router, prefix="/api/v1/quiz", tags=["quiz"])
    app.include_router(review.router, prefix="/api/v1/review", tags=["review"])

    @app.get("/")
    def read_root():
        """Root endpoint."""
        return {
            "name": "文言文实词虚词记忆工具 API",
            "version": "0.1.0",
            "docs": "/docs",
        }

    @app.get("/health")
    def health_check():
        """Health check endpoint."""
        return {"status": "ok"}

    return app
