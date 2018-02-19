# -*- coding: utf-8 -*-

"""Run this script with either :code:`python3 -m bio2bel_interpro deploy`"""

from __future__ import print_function

import logging
import sys

import click

from .constants import DEFAULT_CACHE_CONNECTION
from .deploy import deploy_to_arty
from .interpro_to_go import write_interpro_to_go_bel
from .manager import Manager
from .serialize import write_interpro_tree
from .to_belns import write_belns

log = logging.getLogger(__name__)


@click.group()
@click.option('-c', '--connection', help='Defaults to {}'.format(DEFAULT_CACHE_CONNECTION))
@click.pass_context
def main(ctx, connection):
    """InterPro to BEL"""
    log.setLevel(logging.INFO)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    ctx.obj = Manager(connection=connection)


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
@click.pass_obj
def populate(manager):
    """Populates the database"""
    manager.populate()


@main.command()
@click.option('-y', '--yes', is_flag=True)
@click.pass_obj
def drop(manager, yes):
    """Drops the database"""
    if yes or click.confirm('Drop database?'):
        manager.drop_all()


@main.command()
@click.pass_obj
def web(manager):
    """Run the web app"""
    from .web import get_app
    app = get_app(connection=manager, url='/')
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
