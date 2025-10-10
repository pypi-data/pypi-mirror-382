from __future__ import annotations

from typing import TYPE_CHECKING

from graph_sitter.core.statements.while_statement import WhileStatement
from graph_sitter.shared.decorators.docs import ts_apidoc
from graph_sitter.typescript.interfaces.has_block import TSHasBlock

if TYPE_CHECKING:
    from tree_sitter import Node as TSNode

    from graph_sitter.codebase.codebase_context import CodebaseContext
    from graph_sitter.core.node_id_factory import NodeId
    from graph_sitter.typescript.detached_symbols.code_block import TSCodeBlock


@ts_apidoc
class TSWhileStatement(WhileStatement["TSCodeBlock"], TSHasBlock):
    """A TypeScript while statement class that represents while loops and manages their condition and code block.

    This class provides functionality for handling while statements in TypeScript code,
    including managing the loop's condition and associated code block. It extends the base
    WhileStatement class with TypeScript-specific behavior.

    Attributes:
        condition (str | None): The condition expression of the while loop.
    """

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, ctx: CodebaseContext, parent: TSCodeBlock, pos: int | None = None) -> None:
        super().__init__(ts_node, file_node_id, ctx, parent, pos)
        condition = self.child_by_field_name("condition")
        self.condition = condition.value if condition else None
