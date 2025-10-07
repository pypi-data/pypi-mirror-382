class BaseRepository:
    """Base repository class for flavor-specific data access.

    This repository works with SQLModel sessions and should be extended
    by individual flavors to provide specific data access methods.
    """

    def __init__(self, database_url: str = None, echo: bool = False) -> None:
        """Initialize repository with optional database URL."""
        self.database_url = database_url
        self.echo = echo
        self._engine = None
