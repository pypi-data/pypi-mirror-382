from importlib import metadata
import sys

from aiohttp import ClientResponseError
import click


try:
    __version__ = metadata.version(__package__) if __package__ else "0.0.0"
except metadata.PackageNotFoundError:
    __version__ = "0.0.0"


def main() -> None:
    from zet.cli import zet

    try:
        zet()
    except ClientResponseError as ex:
        click.secho(f"Server returned HTTP {ex.status} {ex.message}", fg="red")
        sys.exit(1)
