# -*- coding: utf-8 -*-

"""Run this script with either :code:`python3 -m bio2bel_interpro arty`"""

from __future__ import print_function

import logging
import sys

import click

from bio2bel_interpro.run import deploy_to_arty, write_belns
from bio2bel_interpro.database.database import Manager

@click.group()
def main():
    """Output gene family hierarchy as BEL script and BEL namespace"""
    logging.basicConfig(level=10, format="%(asctime)s - %(levelname)s - %(message)s")


@main.command()
def arty():
    """Deploy to artifactory"""
    deploy_to_arty()


@main.command()
@click.option('-o', '--output', type=click.File('w'), default=sys.stdout)
def write(output):
    """Writes BEL namespace to standard out"""
    write_belns(output)

@main.command()
def wdb():
    """Creates DataBase file"""
    m = Manager()
    m.write_db()

if __name__ == '__main__':
    main()
