from __future__ import annotations

from typing import TYPE_CHECKING, Self, TypeVar, override

from graph_sitter.core.autocommit import commiter, reader
from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.interfaces.has_attribute import HasAttribute
from graph_sitter.enums import SymbolType
from graph_sitter.shared.decorators.docs import noapidoc, ts_apidoc
from graph_sitter.typescript.interfaces.has_block import TSHasBlock
from graph_sitter.typescript.statements.attribute import TSAttribute
from graph_sitter.typescript.symbol import TSSymbol

if TYPE_CHECKING:
    from tree_sitter import Node as TSNode

    from graph_sitter.codebase.codebase_context import CodebaseContext
    from graph_sitter.core.detached_symbols.code_block import CodeBlock
    from graph_sitter.core.expressions import Expression
    from graph_sitter.core.interfaces.has_name import HasName
    from graph_sitter.core.interfaces.importable import Importable
    from graph_sitter.core.node_id_factory import NodeId
    from graph_sitter.core.statements.statement import Statement
    from graph_sitter.typescript.detached_symbols.code_block import TSCodeBlock

Parent = TypeVar("Parent", bound="TSHasBlock")


@ts_apidoc
class TSEnum(TSHasBlock, TSSymbol, HasAttribute[TSAttribute]):
    """Representation of an Enum in TypeScript.

    Attributes:
        symbol_type: The type of symbol, set to SymbolType.Enum.
        body: The expression representing the body of the enum.
        code_block: The code block associated with the enum.
    """

    symbol_type = SymbolType.Enum
    body: Expression[Self]
    code_block: TSCodeBlock

    def __init__(
        self,
        ts_node: TSNode,
        file_id: NodeId,
        ctx: CodebaseContext,
        parent: Statement[CodeBlock[Parent, ...]],
    ) -> None:
        name_node = ts_node.child_by_field_name("name")
        super().__init__(ts_node, file_id, ctx, parent, name_node=name_node)
        self.body = self._parse_expression(ts_node.child_by_field_name("body"))

    @property
    @reader
    def attributes(self) -> list[TSAttribute[Self, None]]:
        """Property that retrieves the attributes of a TypeScript enum.

        Returns the list of attributes defined within the enum's code block.

        Returns:
            list[TSAttribute[Self, None]]: List of TSAttribute objects representing the enum's attributes.
        """
        return self.code_block.attributes

    @reader
    def get_attribute(self, name: str) -> TSAttribute | None:
        """Returns an attribute from the TypeScript enum by its name.

        Args:
            name (str): The name of the attribute to retrieve.

        Returns:
            TSAttribute | None: The attribute with the given name if it exists, None otherwise.
        """
        return next((x for x in self.attributes if x.name == name), None)

    @noapidoc
    @commiter
    def _compute_dependencies(self, usage_type: UsageKind = UsageKind.BODY, dest: HasName | None = None) -> None:
        dest = dest or self.self_dest
        self.body._compute_dependencies(usage_type, dest)

    @property
    @noapidoc
    def descendant_symbols(self) -> list[Importable]:
        return super().descendant_symbols + self.body.descendant_symbols

    @noapidoc
    @reader
    @override
    def resolve_attribute(self, name: str) -> TSAttribute | None:
        return self.get_attribute(name)

    @staticmethod
    @noapidoc
    def _get_name_node(ts_node: TSNode) -> TSNode | None:
        if ts_node.type == "enum_declaration":
            return ts_node.child_by_field_name("name")
        return None
