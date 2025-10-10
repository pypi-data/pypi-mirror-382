"""srcignore package entry points."""

from .main import app


def main() -> None:
    """Invoke the Typer application."""
    app()


__all__ = ["app", "main"]
