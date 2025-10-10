from functools import cached_property
from typing import Self, override

from graph_sitter.compiled.autocommit import commiter
from graph_sitter.core.autocommit import reader, writer
from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.expressions import Expression
from graph_sitter.core.interfaces.editable import Editable
from graph_sitter.core.interfaces.has_name import HasName
from graph_sitter.core.interfaces.unwrappable import Unwrappable
from graph_sitter.shared.decorators.docs import noapidoc, ts_apidoc


@ts_apidoc
class JSXExpression(Unwrappable["Function | JSXElement | JSXProp"]):
    """Abstract representation of TSX/JSX expression"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.statement

    @cached_property
    @reader
    def statement(self) -> Editable[Self] | None:
        """Returns the editable component of this JSX expression.

        Retrieves the editable contained within this JSX expression by accessing the second child node. Returns None if the JSX expression doesn't
        contain an editable object.

        Returns:
            Editable[Self]: A Editable object representing the statement of this JSX expression. None if the object doesn't have an Editable object.
        """
        return self._parse_expression(self.ts_node.named_children[0]) if len(self.ts_node.named_children) > 0 else None

    @commiter
    @noapidoc
    @override
    def _compute_dependencies(self, usage_type: UsageKind, dest: HasName | None = None) -> None:
        if self.statement:
            self.statement._compute_dependencies(usage_type, dest=dest)

    @writer
    def reduce_condition(self, bool_condition: bool, node: Editable) -> None:
        """Simplifies a JSX expression by reducing it based on a boolean condition.


        Args:
            bool_condition (bool): The boolean value to reduce the condition to.

        """
        if self.ts_node.parent.type == "jsx_attribute" and not bool_condition:
            node.edit(self.ctx.node_classes.bool_conversion[bool_condition])
        else:
            self.remove()

    @writer
    @override
    def unwrap(self, node: Expression | None = None) -> None:
        """Removes the brackets from a JSX expression.


        Returns:
            None
        """
        from graph_sitter.typescript.detached_symbols.jsx.element import JSXElement
        from graph_sitter.typescript.detached_symbols.jsx.prop import JSXProp

        if node is None:
            node = self
        if isinstance(self.parent, JSXProp):
            return
        if isinstance(node, JSXExpression | JSXElement | JSXProp):
            for child in self._anonymous_children:
                child.remove()
