from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from graph_sitter.compiled.autocommit import commiter
from graph_sitter.compiled.sort import sort_editables
from graph_sitter.core.autocommit import reader
from graph_sitter.core.statements.statement import Statement, StatementType
from graph_sitter.core.symbol_groups.expression_group import ExpressionGroup
from graph_sitter.python.interfaces.has_block import PyHasBlock
from graph_sitter.shared.decorators.docs import apidoc, noapidoc

if TYPE_CHECKING:
    from tree_sitter import Node as TSNode

    from graph_sitter.codebase.codebase_context import CodebaseContext
    from graph_sitter.core.dataclasses.usage import UsageKind
    from graph_sitter.core.detached_symbols.function_call import FunctionCall
    from graph_sitter.core.interfaces.has_name import HasName
    from graph_sitter.core.node_id_factory import NodeId
    from graph_sitter.python.detached_symbols.code_block import PyCodeBlock


@apidoc
class WithStatement(Statement["PyCodeBlock"], PyHasBlock):
    """Pythons implementation of the with statement.

    Examples:
    with feature_flag_enabled(...):
        # code block

    with open("file.txt") as file:
        # code block

    with (context_manager1 as var1,
          context_manager2 as var2,
          context_manager3 as var3):
        # code block

    Attributes:
        code_block: The code block of the with statement.
        clause: The expression of the with clause.
    """

    statement_type = StatementType.WITH_STATEMENT
    code_block: PyCodeBlock[WithStatement]
    clause: ExpressionGroup

    def __init__(self, ts_node: TSNode, file_node_id: NodeId, ctx: CodebaseContext, parent: PyCodeBlock, pos: int | None = None) -> None:
        super().__init__(ts_node, file_node_id, ctx, parent, pos)
        self.code_block = self._parse_code_block()
        self.code_block.parse()
        clause = next(x for x in self.ts_node.children if x.type == "with_clause")
        items = [self._parse_expression(item.child_by_field_name("value")) for item in clause.children if item.type == "with_item"]
        self.clause = ExpressionGroup(self.file_node_id, self.ctx, self, children=items)

    @property
    @reader
    def function_calls(self) -> list[FunctionCall]:
        """Returns all function calls in the code block and within the with clause.

        Retrieves all function calls present in both the statement's code block and its with clause.

        Returns:
            list[FunctionCall]: A list of all function calls in the code block and with clause, ordered by their position in the code.
        """
        fcalls = super().function_calls
        fcalls.extend(self.clause.function_calls)
        return sort_editables(fcalls, dedupe=False)

    @cached_property
    @reader
    def nested_code_blocks(self) -> list[PyCodeBlock]:
        """Returns all nested code blocks within the statement.

        Retrieves a list containing all code blocks that are nested within this statement. For a with statement, this includes its main code block.

        Returns:
            list[PyCodeBlock]: A list containing the code block associated with this statement.
        """
        return [self.code_block]

    @noapidoc
    @commiter
    def _compute_dependencies(self, usage_type: UsageKind | None = None, dest: HasName | None = None) -> None:
        self.clause._compute_dependencies(usage_type, dest)
        self.code_block._compute_dependencies(usage_type, dest)
