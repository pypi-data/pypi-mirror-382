import inspect

from typing import Type

from dependency_injector import providers

from tasteful.base_flavor.base_controller import BaseController
from tasteful.containers.base_flavor_container import BaseFlavorContainer
from tasteful.dependencies.graph import Graph
from tasteful.exceptions.injector import NotAvailableForInjectionExceptionError
from tasteful.repositories import BaseRepository

from .base_config import BaseConfig
from .base_service import BaseService


class BaseFlavor:
    """Base class for all Tasteful application flavors.

    Provides core functionality for defining specialized application components
    with their own configurations, service dependencies, and routing logic.
    """

    _injectable: list[Type]
    container: BaseFlavorContainer
    controller: Type[BaseController]

    def __init__(
        self,
        controller: Type[BaseController] = None,
        services: list[Type[BaseService]] = [],
        repositories: list[Type[BaseRepository]] = [],
        config: Type[BaseConfig] = None,
    ):
        """Initialize a new flavor instance."""
        self._injectable = services + repositories

        self.container = BaseFlavorContainer()

        if config:
            self.config = self._create_config(config)

        _graph = Graph(injectable_classes=self._injectable)
        _graph.resolve_dependencies()
        _dependencies = _graph.get_dep_order()

        self._register_dependencies(_dependencies)

        self.controller = self._create_controller(controller)

    def _register_dependencies(self, dependencies: list[Type]) -> None:
        """Register every services within the flavor's container."""
        for dependency in dependencies:
            self._register_dependency(dependency=dependency)

    def _register_dependency(self, dependency: Type) -> None:
        """Create an appropriate provider for a service within the flavor's container."""
        if dependency not in self._injectable:
            raise NotAvailableForInjectionExceptionError(
                f"Service {dependency} is not registered in the list of "
                f"injectable service of flavor {self.__class__.__name__}."
            )

        constructor_args = self._resolve_constructor_dependencies(dependency)

        setattr(
            self.container,
            dependency.__name__,
            providers.Singleton(dependency, **constructor_args),
        )

    def _resolve_constructor_dependencies(self, target_class: Type) -> dict:
        """Extract and resolve constructor dependencies for a class."""
        constructor_params = list(
            inspect.signature(target_class.__init__).parameters.values()
        )[1:]  # Exclude 'self' parameter

        # Filter out variadic parameters (*args, **kwargs)
        constructor_params = [
            param for param in constructor_params if param.name not in ["args", "kwargs"]
        ]

        dependency_providers = {}

        for param in constructor_params:
            dependency_type = param.annotation
            # Only process class types that are in our
            # injectable dependencies and exist in container

            if (
                dependency_type != inspect.Parameter.empty
                and inspect.isclass(dependency_type)
                and dependency_type in self._injectable
                and hasattr(self.container, dependency_type.__name__)
            ):
                dependency_providers[param.name] = getattr(
                    self.container, dependency_type.__name__
                ).provided

        return dependency_providers

    def _create_controller(
        self, controller: Type[BaseController]
    ) -> Type[BaseController]:
        dependency_providers = self._resolve_constructor_dependencies(controller)

        setattr(
            self.container,
            controller.__name__,
            providers.Singleton(controller, **dependency_providers),
        )

        return getattr(self.container, controller.__name__)()

    def _create_config(self, config: Type[BaseConfig]) -> BaseConfig:
        """Create a configuration instance for the flavor."""
        if not issubclass(config, BaseConfig):
            raise TypeError(f"{config} is not a subclass of BaseConfig")

        config_instance = config()

        setattr(self.container, config.__name__, providers.Configuration())
        getattr(self.container, config.__name__).from_pydantic(config_instance)

        self._injectable.append(config)

        return config_instance
