from typing import TypeVar

from tree_sitter import Node as TSNode

from graph_sitter.shared.decorators.docs import ts_apidoc
from graph_sitter.typescript.expressions.named_type import TSNamedType

Parent = TypeVar("Parent")


@ts_apidoc
class TSArrayType(TSNamedType[Parent]):
    """Array type
    Examples:
        string[]
    """

    def _get_name_node(self) -> TSNode | None:
        return self.ts_node.named_children[0]
