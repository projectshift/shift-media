import click, os, sys, shutil
from shiftmedia.cli.colors import *
from click import echo

# -----------------------------------------------------------------------------
# Group setup
# -----------------------------------------------------------------------------


@click.group(help=yellow('Media storage CLI'))
def cli():
    pass


# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------

@cli.command(name='hello')
def hello():
    """ Print welcome """
    echo(yellow('Hello'))