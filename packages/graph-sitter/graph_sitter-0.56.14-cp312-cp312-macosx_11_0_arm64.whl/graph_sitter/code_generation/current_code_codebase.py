# TODO: move out of graph sitter, useful for other projects

import importlib
from pathlib import Path
from typing import TypedDict

from graph_sitter.codebase.config import ProjectConfig
from graph_sitter.configs.models.codebase import CodebaseConfig
from graph_sitter.configs.models.secrets import SecretsConfig
from graph_sitter.core.codebase import Codebase, CodebaseType
from graph_sitter.git.repo_operator.repo_operator import RepoOperator
from graph_sitter.git.schemas.repo_config import RepoConfig
from graph_sitter.shared.decorators.docs import DocumentedObject, apidoc_objects, no_apidoc_objects, py_apidoc_objects, ts_apidoc_objects
from graph_sitter.shared.enums.programming_language import ProgrammingLanguage
from graph_sitter.shared.logging.get_logger import get_logger

logger = get_logger(__name__)


def get_graphsitter_repo_path() -> str:
    """Points to base directory of the Graph-sitter repo (.git) that is currently running"""
    import graph_sitter as sdk

    filepath = sdk.__file__
    codegen_base_dir = filepath.replace("/graph_sitter/__init__.py", "")
    codegen_base_dir = codegen_base_dir.replace("/src", "")
    return codegen_base_dir


def get_codegen_codebase_base_path() -> str:
    import graph_sitter as sdk

    filepath = sdk.__file__
    codegen_base_dir = filepath.replace("/graph_sitter/__init__.py", "")
    return "src" if "src" in codegen_base_dir else ""


def get_current_code_codebase(config: CodebaseConfig | None = None, secrets: SecretsConfig | None = None, subdirectories: list[str] | None = None) -> CodebaseType:
    """Returns a Codebase for the code that is *currently running* (i.e. the Graph-sitter repo)"""
    codegen_repo_path = get_graphsitter_repo_path()
    base_dir = get_codegen_codebase_base_path()
    logger.info(f"Creating codebase from repo at: {codegen_repo_path} with base_path {base_dir}")

    repo_config = RepoConfig.from_repo_path(codegen_repo_path)
    repo_config.respect_gitignore = False
    op = RepoOperator(repo_config=repo_config, bot_commit=False)

    config = (config or CodebaseConfig()).model_copy(update={"base_path": base_dir})
    projects = [ProjectConfig(repo_operator=op, programming_language=ProgrammingLanguage.PYTHON, subdirectories=subdirectories, base_path=base_dir)]
    codebase = Codebase(projects=projects, config=config, secrets=secrets)
    return codebase


def import_all_codegen_sdk_modules():
    # for file in codegen.sdk:

    CODEGEN_SDK_DIR = Path(get_graphsitter_repo_path())
    if base := get_codegen_codebase_base_path():
        CODEGEN_SDK_DIR /= base
    CODEGEN_SDK_DIR /= "graph_sitter"
    for file in CODEGEN_SDK_DIR.rglob("*.py"):
        relative_path = file.relative_to(CODEGEN_SDK_DIR)
        # ignore braintrust_evaluator because it runs stuff on import
        if "__init__" in file.name or "braintrust_evaluator" in file.name:
            continue
        module_name = "graph_sitter." + str(relative_path).replace("/", ".").removesuffix(".py")
        try:
            importlib.import_module(module_name)
        except Exception as e:
            print(f"Error importing {module_name}: {e}")


class DocumentedObjects(TypedDict):
    apidoc: list[DocumentedObject]
    ts_apidoc: list[DocumentedObject]
    py_apidoc: list[DocumentedObject]
    no_apidoc: list[DocumentedObject]


def get_documented_objects() -> DocumentedObjects:
    """Get all the objects decorated with apidoc, py_apidoc, ts_apidoc, and no_apidoc decorators,
    by importing all codegen.sdk modules and keeping track of decorated objects at import time using
    the respective decorators
    """
    import_all_codegen_sdk_modules()
    from graph_sitter.core.codebase import CodebaseType, PyCodebaseType, TSCodebaseType

    if PyCodebaseType not in apidoc_objects:
        apidoc_objects.append(DocumentedObject(name="PyCodebaseType", module="graph_sitter.core.codebase", object=PyCodebaseType))
    if TSCodebaseType not in apidoc_objects:
        apidoc_objects.append(DocumentedObject(name="TSCodebaseType", module="graph_sitter.core.codebase", object=TSCodebaseType))
    if CodebaseType not in apidoc_objects:
        apidoc_objects.append(DocumentedObject(name="CodebaseType", module="graph_sitter.core.codebase", object=CodebaseType))
    return {"apidoc": apidoc_objects, "py_apidoc": py_apidoc_objects, "ts_apidoc": ts_apidoc_objects, "no_apidoc": no_apidoc_objects}
