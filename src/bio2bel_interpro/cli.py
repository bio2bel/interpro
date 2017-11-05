# -*- coding: utf-8 -*-

"""Run this script with either :code:`python3 -m bio2bel_interpro arty`"""

from __future__ import print_function

import logging
import sys

import click

from .database import Manager
from .deploy import deploy_to_arty
from .interpro_to_go import write_interpro_to_go_bel
from .run import write_belns
from .tree import write_interpro_tree


@click.group()
def main():
    """InterPro to BEL"""
    logging.basicConfig(level=10, format="%(asctime)s - %(levelname)s - %(message)s")


@main.command()
@click.option('--force', is_flag=True, help="Force knowledge to be uploaded even if not new namespace")
def deploy(force):
    """Deploy to ArtiFactory"""
    deploy_to_arty(not force)


@main.command()
@click.option('-f', '--file', type=click.File('w'), default=sys.stdout)
def write(file):
    """Writes BEL namespace"""
    write_belns(file=file)


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


@main.command()
@click.option('-c', '--connection', help='Connection to cache. Defaults to {}'.format(Manager.get_connection_string()))
def populate(connection):
    """Populates the database"""
    manager = Manager(connection=connection)
    manager.populate()


if __name__ == '__main__':
    main()
