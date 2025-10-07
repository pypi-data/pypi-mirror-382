from contextlib import contextmanager
from typing import Optional

from sqlmodel import Session, SQLModel, create_engine

from .base_repository import BaseRepository


class SQLModelRepository(BaseRepository):
    """Base repository class for flavor-specific data access.

    This repository works with SQLModel sessions and should be extended
    by individual flavors to provide specific data access methods.
    """

    def __init__(self, database_url: Optional[str] = None, echo: bool = False) -> None:
        """Initialize repository with optional database URL."""
        # TODO: Transform to a database object
        self.database_url = database_url
        self.echo = echo
        if database_url:
            self._engine = create_engine(self.database_url, echo=self.echo)
        else:
            self._engine = None

    @contextmanager
    def get_session(self):
        """Get a database session context manager.

        Usage:
            with repository.get_session() as session:
                # Use session here
                pass

        Yields
        ------
            SQLModel Session instance

        """
        if self._engine is None:
            if not self.database_url:
                raise ValueError("No database URL provided")
            self._engine = create_engine(self.database_url, echo=self.echo)

        # Test connection directly using the engine
        with self._engine.connect() as connection:
            connection.close()

        with Session(self._engine) as session:
            try:
                yield session
            except Exception:
                session.rollback()
                raise

    def create_db_and_tables(self) -> None:
        """Create database tables using SQLModel metadata.

        This should be called after all models are defined.
        """
        if self._engine is None:
            if not self.database_url:
                raise ValueError("No database URL provided")
            self._engine = create_engine(self.database_url, echo=self.echo)

        SQLModel.metadata.create_all(self._engine)
