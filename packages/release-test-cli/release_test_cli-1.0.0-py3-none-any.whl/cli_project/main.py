"""Main CLI entry point."""

import click

# Handle version import for both package and standalone binary
try:
    from . import __version__
except ImportError:
    # When running as a standalone binary, relative imports don't work
    __version__ = "0.5.0"


@click.group()
@click.version_option(version=__version__)
def cli():
    """Release Test CLI Tool."""
    pass


@cli.command()
@click.argument('name')
def greet(name: str):
    """Greet someone by name."""
    click.echo(f"Hello, {name}! This is the CLI tool.")


@cli.command()
def info():
    """Show CLI information."""
    click.echo(f"Release Test CLI v{__version__}")
    click.echo("This is a demo CLI for testing release processes.")


if __name__ == "__main__":
    cli()
    