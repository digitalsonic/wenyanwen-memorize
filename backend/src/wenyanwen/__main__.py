"""CLI entry point for running the server."""

from .main import create_app

app = create_app()


def main() -> None:
    """Run the application using uvicorn."""
    import uvicorn

    from .config import settings

    uvicorn.run(
        "wenyanwen.__main__:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )


if __name__ == "__main__":
    main()
