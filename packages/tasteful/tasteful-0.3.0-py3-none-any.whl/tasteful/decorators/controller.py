from typing import Any, Callable


class EndpointDefinition:
    def __init__(self, method: str = "GET", *args: Any, **kwargs: Any):
        self.method = method
        self.path = args[0] if len(args) > 0 else kwargs.get("path")
        self.args = args[1:]
        self.kwargs = kwargs


class APIControllerDecorator:
    """Emulates FastAPI endpoint decorators for a controller class."""

    def __init__(self, method: str, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs
        self.method = method

    def __call__(self, func: Callable[..., Any]) -> Any:
        """Call the decoration logic when class is placed as a decorators.

        Wraps the decorated function and add hidden `__endpoint_definitions__`
        attributes that contains all the args from the decorator.
        """
        allowed_methods = {
            "delete",
            "get",
            "head",
            "options",
            "patch",
            "post",
            "put",
            "trace",
        }
        if self.method not in allowed_methods:
            return NotImplementedError(
                f"Method {self.method} not allowed in APIController"
            )

        return self._intercept_method(func)

    def _intercept_method(self, endpoint: Callable[..., Any]) -> Callable[..., Any]:
        if not hasattr(endpoint, "__endpoint_definitions__"):
            endpoint.__endpoint_definitions__ = []
        endpoint.__endpoint_definitions__.append(
            EndpointDefinition(self.method, *self.args, **self.kwargs)
        )
        return endpoint


class Get(APIControllerDecorator):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("get", *args, **kwargs)


class Post(APIControllerDecorator):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("post", *args, **kwargs)


class Patch(APIControllerDecorator):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("patch", *args, **kwargs)


class Delete(APIControllerDecorator):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("delete", *args, **kwargs)


class Head(APIControllerDecorator):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("head", *args, **kwargs)


class Options(APIControllerDecorator):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("options", *args, **kwargs)


class Put(APIControllerDecorator):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("put", *args, **kwargs)


class Trace(APIControllerDecorator):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("trace", *args, **kwargs)
