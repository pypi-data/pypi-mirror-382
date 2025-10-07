import sys
import logging

from typing import Any, List, Type

from dependency_injector import providers
from fastapi import FastAPI, Security

from tasteful.base_flavor import BaseFlavor
from tasteful.base_flavor.base_service import BaseService
from tasteful.config import TastefulConfig
from tasteful.containers.tasteful_container import TastefulContainer
from tasteful.logger import TastefulFormatter
from tasteful.repositories import BaseRepository


class TastefulApp:
    def __init__(
        self,
        name: str = None,
        version: str = None,
        log_level: str = None,
        flavors: List[Type[BaseFlavor]] = [],
        authentication_backends: list[Any] = [],
        authorization_backend: Any = None,
        authentication_middlewares: list[Any] = [],
        authorization_middleware: Any = None,
    ):
        self.container = TastefulContainer()

        self.container.config.from_pydantic(TastefulConfig())

        self.name = name or self.container.config.project.name()
        self.version = version or self.container.config.project.version()
        self.log_level = log_level or self.container.config.project.log_level()

        formatter = TastefulFormatter("%(levelname)s:\t  %(asctime)s.%(msecs)03d %(message)s")
        console_handler = logging.StreamHandler(sys.stdout)
        self.logger = self._configure_logger(self.log_level, formatter, console_handler)

        self.flavors = flavors
        self._register_flavors()


        self.container.config.from_pydantic(TastefulConfig())

        if authentication_backends and not authentication_middlewares:
            ## TODO: Raise warning about deprecation of attribute
            authentication_middlewares = authentication_backends

        if authorization_backend and not authorization_middleware:
            ## TODO: Raise warning about deprecation of attribute
            authorization_middleware = authorization_backend

        # Wrap middlewares in Security if they aren't already
        wrapped_middlewares = [
            middleware if isinstance(middleware, Security) else Security(middleware)
            for middleware in authentication_middlewares
        ]

        dependencies = [*wrapped_middlewares]

        if authorization_middleware:
            if not isinstance(authorization_middleware, Security):
                authorization_middleware = Security(authorization_middleware)
            dependencies.append(authorization_middleware)

        self.app = FastAPI(     
            title=self.name,
            version=self.version,
            log_level=self.log_level,
            dependencies=dependencies,
        )

        self.logger.info(
            "FastAPI application: %s v%s",
            self.name,
            self.version,
            extra={"tasteful_app": self.name},
        )
        self._inject_flavors()

    def _register_flavors(self) -> None:
        """Register all flavors with the app."""
        self.logger.info(
            "Registering %d flavors",
            len(self.flavors),
            extra={"tasteful_app": self.name},
        )
        for flavor_class in self.flavors:
            flavor_name = flavor_class.__name__
            setattr(self.container, flavor_name, providers.Singleton(flavor_class))
            self.logger.debug(
                "Successfully registered flavor: %s",
                flavor_name,
                extra={"tasteful_app": "TastefulApp"},
            )

    def _inject_flavors(self) -> None:
        """Inject flavors routes into the FastAPI application."""
        for flavor in self.flavors:
            flavor_name = flavor.__name__
            instance = getattr(self.container, flavor_name)()
            self.app.include_router(instance.controller.router)

            route_count = len(instance.controller.router.routes)
            service_count = 0
            repo_count = 0

            if hasattr(instance, "_injectable"):
                for injectable in instance._injectable:
                    if issubclass(injectable, BaseService):
                        service_count += 1
                    elif issubclass(injectable, BaseRepository):
                        repo_count += 1
            self.logger.info(
                "Injected %d Routes, %d Services, %d Repositories",
                route_count,
                service_count,
                repo_count,
                extra={"flavor": flavor_name},
            )

    def _configure_logger(
        self,
        level: str = "INFO",
        formatter: logging.Formatter = logging.Formatter(),
        console_handler: logging.Handler = logging.StreamHandler(sys.stdout),
    ) -> None:
        """Configure the root logger with the specified level.

        Args:
        ----
            level: The log level to set ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
            formatter: Formatter applied to every handler.
            console_handler: Handler attached to the logger.

        """
        root_logger = logging.getLogger(self.name)
        root_logger.setLevel(level)
        root_logger.addHandler(console_handler)

        # Make sure all handlers use our formatter
        for handler in root_logger.handlers:
            handler.setFormatter(formatter)

        return root_logger