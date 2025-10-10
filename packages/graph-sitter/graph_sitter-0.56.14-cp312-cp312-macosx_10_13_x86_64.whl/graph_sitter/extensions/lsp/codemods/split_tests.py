from typing import TYPE_CHECKING

from graph_sitter.core.function import Function
from graph_sitter.core.interfaces.editable import Editable
from graph_sitter.extensions.lsp.codemods.base import CodeAction

if TYPE_CHECKING:
    from graph_sitter.extensions.lsp.server import GraphSitterLanguageServer


class SplitTests(CodeAction):
    name = "Split Tests"

    def _get_targets(self, server: "GraphSitterLanguageServer", node: Editable) -> dict[Function, str]:
        targets = {}
        for function in node.file.functions:
            if function.name.startswith("test_"):
                target = f"{node.file.directory.path}/{function.name}.py"
                if not server.codebase.has_file(target):
                    targets[function] = target
        return targets

    def is_applicable(self, server: "GraphSitterLanguageServer", node: Editable) -> bool:
        if "tests" in str(node.file.path):
            return len(self._get_targets(server, node)) > 1
        return False

    def execute(self, server: "GraphSitterLanguageServer", node: Editable) -> None:
        targets = self._get_targets(server, node)
        for function, target in targets.items():
            new_file = server.codebase.create_file(target)
            function.move_to_file(new_file, strategy="duplicate_dependencies")
        # node.file.remove()
