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

@cli.command(name='test',context_settings=dict(ignore_unknown_options=True))
@click.argument('nose_argsuments', nargs=-1, type=click.UNPROCESSED)
def test(nose_argsuments):
    """ Run application tests """
    from nose import run
    params = ['__main__', '-c', 'nose.ini']
    params.extend(nose_argsuments)
    run(argv=params)