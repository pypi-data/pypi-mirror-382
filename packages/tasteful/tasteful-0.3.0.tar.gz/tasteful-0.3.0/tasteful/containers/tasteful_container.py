from dependency_injector import containers, providers


class TastefulContainer(containers.DynamicContainer):
    """Dependency injection container for Tasteful application."""

    config = providers.Configuration()
