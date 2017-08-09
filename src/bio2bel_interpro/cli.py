# -*- coding: utf-8 -*-

"""Run this script with either :code:`python3 -m bio2bel_interpro arty`"""

from __future__ import print_function

import logging
import sys

import click

from .database import Manager
from .run import deploy_to_arty, write_belns
from .tree import write_interpro_tree


@click.group()
def main():
    """Output gene family hierarchy as BEL script and BEL namespace"""
    logging.basicConfig(level=10, format="%(asctime)s - %(levelname)s - %(message)s")


@main.command()
def arty():
    """Deploy to ArtiFactory"""
    deploy_to_arty()


@main.command()
@click.option('-o', '--output', type=click.File('w'), default=sys.stdout)
def write(output):
    """Writes BEL namespace"""
    write_belns(output)


@main.command()
@click.option('-o', '--output', type=click.File('w'), default=sys.stdout)
def write_tree(output):
    """Writes the BEL tree"""
    write_interpro_tree(output)


@main.command()
@click.option('-c', '--connection', help='Connection to cache. Defaults to {}'.format(Manager.get_connection_string()))
def populate(connection):
    """Populates the database"""
    manager = Manager(connection=connection)
    manager.populate()


if __name__ == '__main__':
    main()
