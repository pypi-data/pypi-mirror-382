import inspect

from typing import List, Type

from tasteful.exceptions.dependency_graph import CircularDependencyError


class Node:
    """A Node represents a dependency (a class) and all its dependencies (deps)."""

    target_class: Type
    dependencies: List

    def __init__(self, target_class: Type, dependencies: List = None):
        self.target_class = target_class
        self.dependencies = dependencies or []

    def add_dependency(self, dependency_node) -> None:
        """Add a dependency node to the current node's dependencies."""
        self.dependencies.append(dependency_node)

    def __str__(self):
        """Return a string representation of the node."""
        description_parts = (
            f"class = {self.target_class}",
            f"dependencies = {[dep.target_class for dep in self.dependencies]}",
        )
        return "\n".join(description_parts)


class Graph:
    """A Graph represent the whole dependency tree and construct deps in the right order.

    Each node of this graph represents a class and a list of dependencies associated.
    """

    nodes: List[Node]
    unresolved: List[Type]
    resolved: List[Type]

    def __init__(self, injectable_classes: List[Type] = []):
        self.nodes = []
        self.unresolved = []
        self.resolved = []
        self._construct_graph(injectable_classes)

    def _construct_graph(self, injectable_classes: List[Type]) -> None:
        nodes_registry: dict[str, Node] = {}
        # Construct all nodes
        for injectable_class in injectable_classes:
            service_node = nodes_registry.get(injectable_class.__name__)
            if not service_node:
                service_node = Node(target_class=injectable_class, dependencies=[])
                nodes_registry[injectable_class.__name__] = service_node

            service_dependencies = self._get_class_dependencies(injectable_class)

            for dependency_class in service_dependencies:
                dependency_node = nodes_registry.get(dependency_class.__name__)

                if not dependency_node:
                    dependency_node = Node(target_class=dependency_class, dependencies=[])
                    nodes_registry[dependency_class.__name__] = dependency_node

                service_node.add_dependency(dependency_node)

        self.nodes = list(nodes_registry.values())

    def _get_class_dependencies(self, target_class: Type) -> List[Type]:
        constructor_params = list(
            inspect.signature(target_class.__init__).parameters.values()
        )[1:]  # don't care about self arg
        class_dependencies = []
        for param in constructor_params:
            if (
                param.name not in {"args", "kwargs"}
                and param.annotation != inspect.Parameter.empty
                and inspect.isclass(param.annotation)
                # Check the Method Resolution Order (MRO) of the parameter's type to verify 
                # if it inherits from one of the specified base classes.
                and any(
                    base.__name__ in [
                        "BaseService",
                        "BaseRepository",
                        "BaseConfig",
                        "BaseController",
                    ]
                    for base in param.annotation.__mro__
                )  # Only include Tasteful base components
            ):
                class_dependencies.append(param.annotation)

        return class_dependencies

    def resolve_dependencies(self) -> None:
        """Resolve dependencies in the correct order."""
        for node in self.nodes:
            self._resolve_dependencies(node=node)

    def _resolve_dependencies(self, node: Node) -> None:
        """Resolve dependencies for a given node."""
        ## Add it to the seen list
        self.unresolved.append(node.target_class)

        for dependency_node in node.dependencies:
            if dependency_node.target_class not in self.resolved:
                if dependency_node.target_class in self.unresolved:
                    raise CircularDependencyError(
                        (
                            f"Circular dependency detected: "
                            f"{node.target_class.__name__} → "
                            f"{dependency_node.target_class.__name__}"
                        )
                    )
                self._resolve_dependencies(node=dependency_node)

        self.resolved.append(node.target_class)
        self.unresolved.remove(node.target_class)

    def get_dep_order(self) -> List[Type]:
        """Return the resolved dependencies in the correct order."""
        # Emulated OrderedSet
        return list(dict.fromkeys(self.resolved))
