from abc import abstractmethod
from collections.abc import Generator
from typing import TYPE_CHECKING, Generic, Self, TypeVar, override

from tree_sitter import Node as TSNode

from graph_sitter.codebase.resolution_stack import ResolutionStack
from graph_sitter.core.autocommit import commiter, reader, writer
from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.expressions import Name, String
from graph_sitter.core.expressions.type import Type
from graph_sitter.core.interfaces.has_name import HasName
from graph_sitter.core.interfaces.importable import Importable
from graph_sitter.core.interfaces.resolvable import Resolvable
from graph_sitter.core.node_id_factory import NodeId
from graph_sitter.shared.decorators.docs import apidoc, noapidoc

if TYPE_CHECKING:
    from graph_sitter.codebase.codebase_context import CodebaseContext
    from graph_sitter.core.interfaces.editable import Editable

Parent = TypeVar("Parent", bound="Editable")


@apidoc
class NamedType(Resolvable, Type[Parent], HasName, Generic[Parent]):
    """An abstract representation of a named type."""

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, ctx: "CodebaseContext", parent: Parent):
        super().__init__(ts_node, file_node_id, ctx, parent)
        self._name_node = self._parse_expression(self._get_name_node(), default=Name)

    def __eq__(self, other: object) -> bool:
        from graph_sitter.core.symbol import Symbol

        if isinstance(other, Symbol):
            for resolved in self.resolved_types:
                if other == resolved:
                    return True
        return super().__eq__(other)

    def __hash__(self) -> int:
        # needed so this class is hashable
        return super().__hash__()

    @abstractmethod
    def _get_name_node(self) -> TSNode:
        pass

    @reader
    @noapidoc
    @override
    def _resolved_types(self) -> Generator[ResolutionStack[Self], None, None]:
        if name := self.get_name():
            yield from self.with_resolution_frame(name)

    @noapidoc
    @commiter
    def _compute_dependencies(self, usage_type: UsageKind, dest: Importable):
        if isinstance(self.get_name(), String):
            # TODO: string annotations
            self._log_parse("String type annotations are not currently supported")
            return
        self.get_name()._compute_dependencies(usage_type, dest)

    @property
    @noapidoc
    def descendant_symbols(self) -> list["Importable"]:
        """Returns the nested symbols of the importable object, including itself."""
        return self.get_name().descendant_symbols

    @noapidoc
    @writer
    def rename_if_matching(self, old: str, new: str):
        self.get_name().rename_if_matching(old, new)
