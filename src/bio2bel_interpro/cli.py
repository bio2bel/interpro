# -*- coding: utf-8 -*-

"""Run this script with :code:`python3 -m bio2bel_interpro`."""

import logging
import sys

import click

from .manager import Manager
from .serialize import write_interpro_tree

log = logging.getLogger(__name__)

main = Manager.get_cli()


@main.command()
@click.option('-o', '--output', type=click.File('w'), default=sys.stdout)
@click.pass_obj
def write_bel_namespace(manager, output):
    """Write the BEL namespace"""
    manager.write_bel_namespace(output)


@main.command()
@click.option('-f', '--file', type=click.File('w'), default=sys.stdout)
def write_tree(file):
    """Writes the BEL tree"""
    write_interpro_tree(file=file)


if __name__ == '__main__':
    main()
