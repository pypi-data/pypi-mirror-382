from collections.abc import Generator
from typing import TYPE_CHECKING, Generic, Optional, Self, TypeVar, override

from graph_sitter.codebase.resolution_stack import ResolutionStack
from graph_sitter.compiled.autocommit import commiter
from graph_sitter.core.autocommit import reader, writer
from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.expressions import Name
from graph_sitter.core.expressions.expression import Expression
from graph_sitter.core.interfaces.resolvable import Resolvable
from graph_sitter.shared.decorators.docs import apidoc, noapidoc

if TYPE_CHECKING:
    from graph_sitter.core.interfaces.chainable import Chainable
    from graph_sitter.core.interfaces.has_name import HasName


Object = TypeVar("Object", bound="Chainable")
Index = TypeVar("Index", bound="Expression")
Parent = TypeVar("Parent", bound="Expression")


@apidoc
class SubscriptExpression(Expression[Parent], Resolvable[Parent], Generic[Object, Index, Parent]):
    """Indexing onto an object (Aka using brackets on an object)

    Examples:
     A[]

    Attributes:
        object: The object being indexed.
        indices: A list of indices used for indexing the object.

    """

    object: Object
    indices: list[Index]

    def __init__(self, ts_node, file_node_id, ctx, parent: Parent):
        super().__init__(ts_node, file_node_id, ctx, parent=parent)
        self.object = self._parse_expression(self.ts_node.children[0], default=Name)
        self.indices = self.children[1:]

    @reader
    @noapidoc
    @override
    def _resolved_types(self) -> Generator[ResolutionStack[Self], None, None]:
        # TODO: implement this properly
        yield from self.object.resolved_type_frames

    @noapidoc
    @commiter
    def _compute_dependencies(self, usage_type: UsageKind, dest: Optional["HasName | None"] = None) -> None:
        self.object._compute_dependencies(usage_type, dest)
        for index in self.indices:
            index._compute_dependencies(usage_type, dest)

    @writer
    @noapidoc
    def rename_if_matching(self, old: str, new: str) -> None:
        if self.object:
            self.object.rename_if_matching(old, new)
