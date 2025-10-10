#!/bin/python

import click

from graph_sitter.gscli.generate.commands import generate


@click.group()
def main() -> None:
    pass


# ============= Import all command groups =============
main.add_command(generate)


if __name__ == "__main__":
    main()
