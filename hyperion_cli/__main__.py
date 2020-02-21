"""
The main hyperion entry point. Run `hyperion --help` for more info.
"""

import logging
from asyncio import get_event_loop, CancelledError, set_event_loop_policy

import click
import uvloop
from aiohttp import web
from click import Path
from colorama import Fore

from . import logger
from .api import app
from .api.util import enable_cross_origin
from .cli import cli
from .models import util, initialize_database

set_event_loop_policy(uvloop.EventLoopPolicy())


@click.command()
@click.argument('locations', required=False, nargs=-1)
@click.option('--random', '-r', count=True)
@click.option('--bikes', '-b', is_flag=True)
@click.option('--crime', '-c', is_flag=True)
@click.option('--nearby', '-n', is_flag=True)
@click.option('--json', '-j', is_flag=True)
@click.option('--update-bikes', is_flag=True)
@click.option('--api-server', is_flag=True)
@click.option('--cross-origin', is_flag=True)
@click.option('--host', '-h', type=str, default='0.0.0.0')
@click.option('--port', '-p', type=int, default=8000)
@click.option('--db-path', type=Path(dir_okay=False))
@click.option('--verbose', '-v', count=True)
def run_cli(locations, random, bikes, crime, nearby, json, update_bikes, api_server, cross_origin, host, port, db_path,
            verbose):
    """
    Runs the program. Takes a list of postcodes or coordinates and
    returns various information about them. If using the cli, make
    sure to update the bikes database with the -u command.

    Locations can be either a specific postcode, or a pair of coordinates.
    Coordinates are passed in the form "55.948824,-3.196425".

    :param locations: The list of postcodes or coordinates to search.
    :param random: The number of random postcodes to include.
    :param bikes: Includes a list of stolen bikes in that area.
    :param crime: Includes a list of committed crimes in that area.
    :param nearby: Includes a list of wikipedia articles in that area.
    :param json: Returns the data in json format.
    :param update_bikes: Whether to force update bikes.
    :param api_server: If given, the program will instead run a rest api.
    :param cross_origin:
    :param host:
    :param port: Defines the port to run the rest api on.
    :param db_path: The path to the sqlite db to use.
    :param verbose: The verbosity.
    """

    log_levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    logging.basicConfig(level=log_levels[min(verbose, 2)])

    initialize_database(db_path)

    loop = get_event_loop()

    if update_bikes:
        logger.info("Force updating bikes.")
        loop.run_until_complete(util.update_bikes())

    if api_server:
        if cross_origin:
            enable_cross_origin(app)

        try:
            web.run_app(app, host=host, port=port)
        except CancelledError as e:
            if e.__context__ is not None:
                click.echo(Fore.RED + (
                    f"Could not bind to address {host}:{port}" if e.__context__.errno == 48 else e.__context__))
                exit(1)
            else:
                click.echo("Goodbye!")

    elif len(locations) > 0 or random > 0:
        exit(loop.run_until_complete(cli(locations, random, bikes=bikes, crime=crime, nearby=nearby, as_json=json)))
    else:
        click.echo(Fore.RED + "Either include a post code, or the --api-server flag.")


if __name__ == '__main__':
    run_cli()
