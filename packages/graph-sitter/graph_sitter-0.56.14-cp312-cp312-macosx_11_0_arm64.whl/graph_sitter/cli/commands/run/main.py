import json
import os

import rich_click as click

from graph_sitter.cli.auth.session import CliSession
from graph_sitter.cli.utils.codemod_manager import CodemodManager
from graph_sitter.cli.utils.json_schema import validate_json
from graph_sitter.cli.workspace.decorators import requires_init
from graph_sitter.cli.workspace.venv_manager import VenvManager


@click.command(name="run")
@requires_init
@click.argument("label", required=True)
@click.option("--daemon", "-d", is_flag=True, help="Run the function against a running daemon")
@click.option("--diff-preview", type=int, help="Show a preview of the first N lines of the diff")
@click.option("--arguments", type=str, help="Arguments as a json string to pass as the function's 'arguments' parameter")
def run_command(
    session: CliSession,
    label: str,
    daemon: bool = False,
    diff_preview: int | None = None,
    arguments: str | None = None,
):
    """Run a codegen function by its label."""
    # Ensure venv is initialized
    venv = VenvManager(session.codegen_dir)
    if not venv.is_initialized():
        msg = "Virtual environment not found. Please run 'gs init' first."
        raise click.ClickException(msg)

    # Set up environment with venv
    os.environ["VIRTUAL_ENV"] = str(venv.venv_dir)
    os.environ["PATH"] = f"{venv.venv_dir}/bin:{os.environ['PATH']}"

    # Get and validate the codemod
    codemod = CodemodManager.get_codemod(label)

    # Handle arguments if needed
    if codemod.arguments_type_schema and not arguments:
        msg = f"This function requires the --arguments parameter. Expected schema: {codemod.arguments_type_schema}"
        raise click.ClickException(msg)

    if codemod.arguments_type_schema and arguments:
        arguments_json = json.loads(arguments)
        is_valid = validate_json(codemod.arguments_type_schema, arguments_json)
        if not is_valid:
            msg = f"Invalid arguments format. Expected schema: {codemod.arguments_type_schema}"
            raise click.ClickException(msg)

    # Run the codemod
    if daemon:
        from graph_sitter.cli.commands.run.run_daemon import run_daemon

        run_daemon(session, codemod, diff_preview=diff_preview)
    else:
        from graph_sitter.cli.commands.run.run_local import run_local

        run_local(session, codemod, diff_preview=diff_preview)
