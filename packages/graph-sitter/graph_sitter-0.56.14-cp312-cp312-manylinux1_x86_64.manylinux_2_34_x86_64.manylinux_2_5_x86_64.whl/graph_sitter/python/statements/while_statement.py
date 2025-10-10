from __future__ import annotations

from typing import TYPE_CHECKING

from graph_sitter.compiled.autocommit import commiter, reader
from graph_sitter.compiled.sort import sort_editables
from graph_sitter.core.statements.while_statement import WhileStatement
from graph_sitter.python.interfaces.has_block import PyHasBlock
from graph_sitter.python.statements.if_block_statement import PyIfBlockStatement
from graph_sitter.shared.decorators.docs import noapidoc, py_apidoc

if TYPE_CHECKING:
    from tree_sitter import Node as TSNode

    from graph_sitter.codebase.codebase_context import CodebaseContext
    from graph_sitter.core.dataclasses.usage import UsageKind
    from graph_sitter.core.detached_symbols.function_call import FunctionCall
    from graph_sitter.core.interfaces.has_name import HasName
    from graph_sitter.core.interfaces.importable import Importable
    from graph_sitter.core.node_id_factory import NodeId
    from graph_sitter.python.detached_symbols.code_block import PyCodeBlock


@py_apidoc
class PyWhileStatement(WhileStatement["PyCodeBlock"], PyHasBlock):
    """An abstract representation of a python while statement.

    Attributes:
        else_statement (PyIfBlockStatement | None): the statement that will run if the while loop completes, if any.
    """

    else_statement: PyIfBlockStatement[PyCodeBlock[PyWhileStatement]] | None = None

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, ctx: CodebaseContext, parent: PyCodeBlock, pos: int | None = None) -> None:
        super().__init__(ts_node, file_node_id, ctx, parent, pos)
        self.condition = self.child_by_field_name("condition")
        if else_block := ts_node.child_by_field_name("alternative"):
            self.else_statement = PyIfBlockStatement(else_block, file_node_id, ctx, self.code_block, self.index, main_if_block=self)
        else:
            self.else_statement = None

    @property
    @reader
    def nested_code_blocks(self) -> list[PyCodeBlock]:
        """Returns a list of all code blocks nested within the while statement.

        Returns all code blocks contained within this while statement, including blocks from the else statement
        if it exists. The first block in the list is always the main while statement's code block.

        Returns:
            list[PyCodeBlock]: A list of code blocks contained within this statement, including those in the else branch.
        """
        blocks = [self.code_block]
        if self.else_statement:
            blocks.extend(self.else_statement.nested_code_blocks)
        return blocks

    @property
    @reader
    def function_calls(self) -> list[FunctionCall]:
        """Returns all function calls within the while statement and its else block.

        Returns a list of FunctionCall objects representing all function calls found in both the while statement's
        code block and its else block (if it exists). Function calls are sorted but not deduplicated.

        Returns:
            list[FunctionCall]: A sorted list of FunctionCall objects representing all function calls within the
                while statement and its else block.
        """
        fcalls = super().function_calls
        if self.else_statement:
            fcalls.extend(self.else_statement.function_calls)
        return sort_editables(fcalls, dedupe=False)

    @noapidoc
    @commiter
    def _compute_dependencies(self, usage_type: UsageKind | None = None, dest: HasName | None = None) -> None:
        super()._compute_dependencies(usage_type, dest)
        if self.else_statement:
            self.else_statement._compute_dependencies(usage_type, dest)

    @property
    @noapidoc
    def descendant_symbols(self) -> list[Importable]:
        symbols = super().descendant_symbols
        symbols.extend(self.code_block.descendant_symbols)
        if self.else_statement:
            symbols.extend(self.else_statement.descendant_symbols)
        return symbols
