from typing import Generic, TypeVar

from tree_sitter import Node as TSNode

from graph_sitter.core.expressions.named_type import NamedType
from graph_sitter.shared.decorators.docs import py_apidoc

Parent = TypeVar("Parent")


@py_apidoc
class PyNamedType(NamedType[Parent], Generic[Parent]):
    """Named python type

    Examples:
        int,str (builtin types)
        Path (classes)
    """

    def _get_name_node(self) -> TSNode | None:
        return self.ts_node
