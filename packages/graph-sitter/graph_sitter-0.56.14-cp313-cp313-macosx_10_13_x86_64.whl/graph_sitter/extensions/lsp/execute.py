from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from lsprotocol import types
from lsprotocol.types import Position, Range

from graph_sitter.extensions.lsp.codemods.base import CodeAction
from graph_sitter.shared.logging.get_logger import get_logger

if TYPE_CHECKING:
    from graph_sitter.extensions.lsp.server import GraphSitterLanguageServer

logger = get_logger(__name__)


def process_args(args: Any) -> tuple[str, Range]:
    uri = args[0]
    range = args[1]
    range = Range(start=Position(line=range["start"]["line"], character=range["start"]["character"]), end=Position(line=range["end"]["line"], character=range["end"]["character"]))
    return uri, range


def execute_action(server: "GraphSitterLanguageServer", action: CodeAction, args: Any) -> None:
    uri, range = process_args(args)
    node = server.get_node_under_cursor(uri, range.start, range.end)
    if node is None:
        logger.warning(f"No node found for range {range}")
        return
    action.execute(server, node, *args[2:])
    server.codebase.commit()


def get_execute_action(action: CodeAction) -> Callable[["GraphSitterLanguageServer", Any], None]:
    def execute_action(server: "GraphSitterLanguageServer", args: Any) -> None:
        logger.info(f"Executing action {action.command_name()} with args {args}")
        execute_action(server, action, args)
        server.workspace_apply_edit(types.ApplyWorkspaceEditParams(edit=server.io.get_workspace_edit())).result()

    return execute_action
