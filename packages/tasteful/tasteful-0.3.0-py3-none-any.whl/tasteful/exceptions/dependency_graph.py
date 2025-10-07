class CircularDependencyError(Exception):
    """Exception raised when a circular dependency is detected in the dependency graph."""

    def __init__(self, message="Circular dependency detected in the dependency graph"):
        self.message = message
        super().__init__(self.message)
