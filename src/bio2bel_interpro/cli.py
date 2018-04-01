# -*- coding: utf-8 -*-

"""Run this script with either :code:`python3 -m bio2bel_interpro deploy`"""

from __future__ import print_function

import logging
import sys

import click

from bio2bel.cli_utils import build_cli
from .interpro_to_go import write_interpro_to_go_bel
from .manager import Manager
from .serialize import write_interpro_tree

log = logging.getLogger(__name__)

main = build_cli(Manager)


@main.command()
@click.option('-o', '--output', type=click.File('w'), default=sys.stdout)
@click.pass_obj
def write_bel_namespace(manager, output):
    """Write the BEL namespace"""
    manager.write_bel_namespace(output)


@main.command()
@click.option('-o', '--output', type=click.File('w'), default=sys.stdout)
@click.pass_obj
def deploy_bel_namespace(manager):
    """Deploy the BEL namespace"""
    manager.deploy_bel_namespace()


@main.command()
@click.option('-f', '--file', type=click.File('w'), default=sys.stdout)
def write_tree(file):
    """Writes the BEL tree"""
    write_interpro_tree(file=file)


@main.command()
@click.option('-f', '--file', type=click.File('w'), default=sys.stdout)
def write_go_mapping(file):
    """Writes the InterPro to Gene Ontology mapping as a BEL Script"""
    write_interpro_to_go_bel(file=file)


if __name__ == '__main__':
    main()
