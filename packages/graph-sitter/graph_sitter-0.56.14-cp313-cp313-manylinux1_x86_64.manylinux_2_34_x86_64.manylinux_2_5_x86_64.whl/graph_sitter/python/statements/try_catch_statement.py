from __future__ import annotations

from typing import TYPE_CHECKING, Self, override

from graph_sitter.compiled.autocommit import commiter, reader
from graph_sitter.core.statements.try_catch_statement import TryCatchStatement
from graph_sitter.python.statements.block_statement import PyBlockStatement
from graph_sitter.python.statements.catch_statement import PyCatchStatement
from graph_sitter.shared.decorators.docs import noapidoc, py_apidoc

if TYPE_CHECKING:
    from collections.abc import Sequence

    from tree_sitter import Node as PyNode

    from graph_sitter.codebase.codebase_context import CodebaseContext
    from graph_sitter.core.dataclasses.usage import UsageKind
    from graph_sitter.core.detached_symbols.function_call import FunctionCall
    from graph_sitter.core.interfaces.conditional_block import ConditionalBlock
    from graph_sitter.core.interfaces.has_name import HasName
    from graph_sitter.core.interfaces.importable import Importable
    from graph_sitter.core.node_id_factory import NodeId
    from graph_sitter.python.detached_symbols.code_block import PyCodeBlock


@py_apidoc
class PyTryCatchStatement(TryCatchStatement["PyCodeBlock"], PyBlockStatement):
    """Abstract representation of the try/catch/finally block in Python.

    Attributes:
        except_clauses: The exception handlers.
    """

    except_clauses: list[PyCatchStatement[Self]]

    def __init__(self, ts_node: PyNode, file_node_id: NodeId, ctx: CodebaseContext, parent: PyCodeBlock, pos: int | None = None) -> None:
        super().__init__(ts_node, file_node_id, ctx, parent, pos)
        self.except_clauses = []
        for node in self.ts_node.named_children:
            if node.type == "finally_clause":
                self.finalizer = PyBlockStatement(node, file_node_id, ctx, self, self.index)
            elif node.type == "except_clause":
                self.except_clauses.append(PyCatchStatement(node, file_node_id, ctx, self, self.index))

    @property
    @reader
    def function_calls(self) -> list[FunctionCall]:
        """Gets a list of all function calls contained within the try-catch statement.

        Returns a list of function calls from all parts of the try-catch statement, including the main block, all except clauses, and the finally block if it exists.

        Returns:
            list[FunctionCall]: A list of all function calls found in the try-catch statement, its except clauses, and finally block.
        """
        fcalls = super().function_calls
        for clause in self.except_clauses:
            fcalls.extend(clause.function_calls)
        if self.finalizer:
            fcalls.extend(self.finalizer.function_calls)
        return fcalls

    @noapidoc
    @commiter
    def _compute_dependencies(self, usage_type: UsageKind | None = None, dest: HasName | None = None) -> None:
        super()._compute_dependencies(usage_type, dest)
        for clause in self.except_clauses:
            clause._compute_dependencies(usage_type, dest)
        if self.finalizer:
            self.finalizer._compute_dependencies(usage_type, dest)

    @property
    @noapidoc
    def descendant_symbols(self) -> list[Importable]:
        symbols = super().descendant_symbols
        for clause in self.except_clauses:
            symbols.extend(clause.descendant_symbols)
        if self.finalizer:
            symbols.extend(self.finalizer.descendant_symbols)
        return symbols

    @property
    @reader
    @override
    def nested_code_blocks(self) -> list[PyCodeBlock]:
        """Returns all CodeBlocks nested within this try-catch statement.

        Retrieves a list of code blocks from the try block, except clauses, and finally block (if present).

        Returns:
            list[PyCodeBlock]: A list containing all nested code blocks in the following order:
                - try block
                - nested blocks within finally block (if present)
                - except clause blocks
                - finally block (if present)
        """
        nested_blocks = [self.code_block, *self.finalizer.nested_code_blocks] if self.finalizer else [self.code_block]
        for except_clause in self.except_clauses:
            nested_blocks.append(except_clause.code_block)
        if self.finalizer:
            nested_blocks.append(self.finalizer.code_block)
        return nested_blocks

    @property
    @noapidoc
    def other_possible_blocks(self) -> Sequence[ConditionalBlock]:
        return self.except_clauses
