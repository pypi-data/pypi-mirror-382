from graph_sitter.core.autocommit import commiter, reader
from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.interfaces.has_name import HasName
from graph_sitter.core.type_alias import TypeAlias
from graph_sitter.enums import SymbolType
from graph_sitter.shared.decorators.docs import noapidoc, ts_apidoc
from graph_sitter.typescript.detached_symbols.code_block import TSCodeBlock
from graph_sitter.typescript.interfaces.has_block import TSHasBlock
from graph_sitter.typescript.statements.attribute import TSAttribute
from graph_sitter.typescript.symbol import TSSymbol


@ts_apidoc
class TSTypeAlias(TypeAlias[TSCodeBlock, TSAttribute], TSSymbol, TSHasBlock):
    """Representation of an Interface in TypeScript.

    Attributes:
        symbol_type: The type of symbol, set to SymbolType.Type.
    """

    symbol_type = SymbolType.Type

    @noapidoc
    @commiter
    def _compute_dependencies(self, usage_type: UsageKind | None = None, dest: HasName | None = None) -> None:
        dest = dest or self.self_dest
        # =====[ Type Identifiers ]=====
        # Look for type references in the interface body
        self.value._compute_dependencies(UsageKind.TYPE_DEFINITION, dest)
        self.code_block._compute_dependencies(UsageKind.TYPE_DEFINITION, dest)
        # body = self.ts_node.child_by_field_name("value")
        # if body:
        #     # Handle type queries (typeof)
        #     type_queries = find_all_descendants(body, ["type_query"])
        #     for type_query in type_queries:
        #         query_identifiers = find_all_descendants(type_query, ["identifier"])
        #         self._add_symbol_usages(query_identifiers, SymbolUsageType.TYPE)
        #
        #     type_identifiers = find_all_descendants(body, ["type_identifier"])
        #     self._add_symbol_usages(type_identifiers, SymbolUsageType.TYPE)
        if self.type_parameters:
            self.type_parameters._compute_dependencies(UsageKind.GENERIC, dest)

    @reader
    def _parse_code_block(self) -> TSCodeBlock:
        """Returns the code block of the function"""
        value_node = self.ts_node.child_by_field_name("value")
        return super()._parse_code_block(value_node)

    @property
    @reader
    def attributes(self) -> list[TSAttribute]:
        """Retrieves all attributes belonging to this type alias.

        Returns a list of attributes that are defined within the type alias's code block.
        These attributes represent named values or properties associated with the type alias.

        Returns:
            list[TSAttribute[TSTypeAlias, None]]: A list of TSAttribute objects representing the type alias's attributes.
        """
        return self.code_block.attributes

    @reader
    def get_attribute(self, name: str) -> TSAttribute | None:
        """Retrieves a specific attribute from a TypeScript type alias by its name.

        Args:
            name (str): The name of the attribute to retrieve.

        Returns:
            TSAttribute[TSTypeAlias, None] | None: The attribute with the specified name if found, None otherwise.
        """
        return next((x for x in self.attributes if x.name == name), None)
