import click

from blazetest import __version__


@click.group()
@click.version_option(__version__, "-v", "--version")
@click.help_option("-h", "--help")
def cli():
    pass
