from lsprotocol.types import Position

from graph_sitter.core.assignment import Assignment
from graph_sitter.core.detached_symbols.function_call import FunctionCall
from graph_sitter.core.expressions.chained_attribute import ChainedAttribute
from graph_sitter.core.expressions.expression import Expression
from graph_sitter.core.expressions.name import Name
from graph_sitter.core.interfaces.editable import Editable
from graph_sitter.core.interfaces.has_name import HasName
from graph_sitter.shared.logging.get_logger import get_logger

logger = get_logger(__name__)


def go_to_definition(node: Editable | None, uri: str, position: Position) -> Editable | None:
    if node is None or not isinstance(node, (Expression)):
        logger.warning(f"No node found at {uri}:{position}")
        return None
    if isinstance(node, Name) and isinstance(node.parent, ChainedAttribute) and node.parent.attribute == node:
        node = node.parent
    if isinstance(node.parent, FunctionCall) and node.parent.get_name() == node:
        node = node.parent
    logger.info(f"Resolving definition for {node}")
    if isinstance(node, FunctionCall):
        resolved = node.function_definition
    else:
        resolved = node.resolved_value
    if resolved is None:
        logger.warning(f"No resolved value found for {node.name} at {uri}:{position}")
        return None
    if isinstance(resolved, HasName):
        resolved = resolved.get_name()
    if isinstance(resolved.parent, Assignment) and resolved.parent.value == resolved:
        resolved = resolved.parent.get_name()
    return resolved
