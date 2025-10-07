import inspect

from typing import Any

from fastapi import APIRouter


class BaseController:
    def __init__(self, prefix: str = "", tags: list = []):
        self.prefix = prefix
        self.tags = tags
        self.router = APIRouter(prefix=self.prefix, tags=self.tags)
        self._router_from_controller()

    def _router_from_controller(self, **defaults_route_args: Any) -> None:
        """Build a router from a controller instance annotated endpoints).

        Args:
        ----
            defaults_route_args: Default arguments to pass to all routes

        """
        # Find all methods that have endpoint definitions attached
        members = inspect.getmembers(
            self, lambda x: hasattr(x, "__endpoint_definitions__")
        )

        # Register each endpoint with the router
        for _, endpoint in members:
            for endpoint_definition in getattr(endpoint, "__endpoint_definitions__"):
                kwargs = {**defaults_route_args, **endpoint_definition.kwargs}

                self.router.add_api_route(
                    endpoint_definition.path,
                    endpoint,
                    methods=[endpoint_definition.method],
                    **kwargs,
                )
