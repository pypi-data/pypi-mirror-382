from collections.abc import Generator
from typing import TYPE_CHECKING, Generic, Self, TypeVar, override

from tree_sitter import Node as TSNode

from graph_sitter.codebase.resolution_stack import ResolutionStack
from graph_sitter.core.autocommit import reader
from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.expressions.type import Type
from graph_sitter.core.interfaces.importable import Importable
from graph_sitter.core.node_id_factory import NodeId
from graph_sitter.shared.decorators.docs import noapidoc, ts_apidoc

if TYPE_CHECKING:
    from graph_sitter.codebase.codebase_context import CodebaseContext
    from graph_sitter.typescript.expressions.type import TSType


Parent = TypeVar("Parent")


@ts_apidoc
class TSConditionalType(Type[Parent], Generic[Parent]):
    """Conditional Type

    Examples:
    typeof s

    Attributes:
        left: The left-hand side type of the conditional type.
        right: The right-hand side type of the conditional type.
        consequence: The type if the condition is true.
        alternative: The type if the condition is false.
    """

    left: "TSType[Self]"
    right: "TSType[Self]"
    consequence: "TSType[Self]"
    alternative: "TSType[Self]"

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, ctx: "CodebaseContext", parent: Parent):
        super().__init__(ts_node, file_node_id, ctx, parent)
        self.left = self.child_by_field_name("left")
        self.right = self.child_by_field_name("right")
        self.consequence = self.child_by_field_name("consequence")
        self.alternative = self.child_by_field_name("alternative")

    def _compute_dependencies(self, usage_type: UsageKind, dest: Importable):
        self.left._compute_dependencies(usage_type, dest)
        self.right._compute_dependencies(usage_type, dest)
        self.consequence._compute_dependencies(usage_type, dest)
        self.alternative._compute_dependencies(usage_type, dest)

    @reader
    @noapidoc
    @override
    def _resolved_types(self) -> Generator[ResolutionStack[Self], None, None]:
        yield from self.with_resolution_frame(self.consequence)
        yield from self.with_resolution_frame(self.alternative)
