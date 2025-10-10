from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Generic

from typing_extensions import TypeVar

from graph_sitter.core.autocommit import reader
from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.expressions import Expression
from graph_sitter.core.expressions.name import Name
from graph_sitter.core.interfaces.has_name import HasName
from graph_sitter.shared.decorators.docs import apidoc, noapidoc

if TYPE_CHECKING:
    from tree_sitter import Node as TSNode

    from graph_sitter.core.class_definition import Class
    from graph_sitter.core.detached_symbols.function_call import FunctionCall
    from graph_sitter.core.detached_symbols.parameter import Parameter
    from graph_sitter.core.function import Function


TClass = TypeVar("TClass", bound="Class", default="Class")
TFunction = TypeVar("TFunction", bound="Function", default="Function")
TParameter = TypeVar("TParameter", bound="Parameter", default="Parameter")


@apidoc
class Decorator(Expression[TClass | TFunction], HasName, Generic[TClass, TFunction, TParameter]):
    """Abstract representation of a Decorator."""

    def __init__(self, ts_node: TSNode, parent: TClass | TFunction) -> None:
        super().__init__(ts_node, parent.file_node_id, parent.ctx, parent)
        self._name_node = self._parse_expression(self._get_name_node(), default=Name)

    @abstractmethod
    @reader
    @noapidoc
    def _get_name_node(self) -> TSNode:
        """Returns the TSNode of the name of the decorator."""

    @property
    @reader
    @abstractmethod
    def call(self) -> FunctionCall | None:
        """Returns any function call made by this decorator.

        This property identifies whether a decorator makes a function call and provides access to the call details.

        Returns:
            FunctionCall | None: The FunctionCall object representing the function call made by the decorator if one exists,
                None if the decorator does not make a function call.
        """

    def _compute_dependencies(self, usage_type: UsageKind | None = None, dest: HasName | None = None) -> None:
        self._add_all_identifier_usages(UsageKind.DECORATOR, dest or self.parent.self_dest)
