import inspect
from enum import StrEnum
from itertools import chain

from graph_sitter.code_generation.current_code_codebase import get_documented_objects
from graph_sitter.core import codebase


class LanguageType(StrEnum):
    PYTHON = "PYTHON"
    TYPESCRIPT = "TYPESCRIPT"
    BOTH = "BOTH"


def generate_builtins_file(path_to_builtins: str, language_type: LanguageType):
    """Generates and writes the builtins file"""
    documented_imports = get_documented_objects()
    all_objects = chain(documented_imports["apidoc"], documented_imports["py_apidoc"], documented_imports["ts_apidoc"])
    unique_imports = {f"from {obj.module} import {obj.name} as {obj.name}" for obj in all_objects}
    all_imports = "\n".join(sorted(unique_imports))
    # TODO: re-use code with runner_imports list
    # TODO: also auto generate import string for CodemodContext + MessageType

    if language_type == LanguageType.PYTHON:
        codebase_type = "PyCodebaseType"
    elif language_type == LanguageType.TYPESCRIPT:
        codebase_type = "TSCodebaseType"
    else:  # BOTH
        codebase_type = "PyCodebaseType | TSCodebaseType"

    BUILTINS_FILE_TEMPLATE = f"""
# This file is auto-generated, do not modify manually

{{all_imports}}
from graph_sitter.git.models.codemod_context import CodemodContext
from graph_sitter.git.models.pr_options import PROptions
from graph_sitter.git.models.github_named_user_context import GithubNamedUserContext
from graph_sitter.git.models.pr_part_context import PRPartContext
from graph_sitter.git.models.pull_request_context import PullRequestContext
from graph_sitter.codebase.flagging.code_flag import MessageType as MessageType

{"\n".join(inspect.getsource(codebase).splitlines()[-2:])}
CodebaseType = {codebase_type}

# declare global type for 'codebase'
codebase: CodebaseType

# declare global type for 'context'
context: CodemodContext

pr_options: PROptions
"""

    with open(path_to_builtins, "w") as f:
        f.write(BUILTINS_FILE_TEMPLATE.format(all_imports=all_imports))
