# -*- coding: utf-8 -*-

"""Run this script with either :code:`python3 -m bio2bel_interpro arty`"""

from __future__ import print_function

import logging
import sys

import click

from .constants import DEFAULT_CACHE_CONNECTION
from .manager import Manager
from .deploy import deploy_to_arty
from .interpro_to_go import write_interpro_to_go_bel
from .to_belns import write_belns
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
@click.option('-c', '--connection', help='Connection to cache. Defaults to {}'.format(DEFAULT_CACHE_CONNECTION))
def populate(connection):
    """Populates the database"""
    manager = Manager(connection=connection)
    manager.populate_entries()


@main.command()
@click.option('-c', '--connection', help='Connection to cache. Defaults to {}'.format(DEFAULT_CACHE_CONNECTION))
def drop(connection):
    """Drops the database"""
    manager = Manager(connection=connection)
    manager.drop_all()


@main.command()
def web():
    """Run the web app"""
    from .web import app
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
