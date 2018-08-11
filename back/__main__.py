#!/usr/bin/env python
import asyncio
import logging

import click
from aiohttp import web
from colorama import Fore
from sys import exit

from back.api import app
from back.cli import cli

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@click.command()
@click.argument('postcodes', required=False, nargs=-1)
@click.option('--bikes', '-b', is_flag=True)
@click.option('--crime', '-c', is_flag=True)
@click.option('--nearby', '-n', is_flag=True)
@click.option('--json', '-j', is_flag=True)
@click.option('--api-server', '-a', is_flag=True)
@click.option('--port', '-p', type=int, default=8000)
def run(postcodes, bikes, crime, nearby, json, api_server, port):
    """
    Runs the program.

    :param postcodes: The postcode to search.
    :param bikes: Includes a list of stolen bikes in that area.
    :param crime: Includes a list of committed crimes in that area.
    :param nearby: Includes a list of wikipedia articles in that area.
    :param json: Returns the data in json format.
    :param api_server: If given, the program will instead run a rest api.
    :param port: Defines the port to run the rest api on.
    """

    if api_server:
        web.run_app(app, host='0.0.0.0', port=port)
    elif len(postcodes) > 0:
        loop = asyncio.get_event_loop()
        exit(loop.run_until_complete(cli(postcodes, bikes, crime, nearby, json)))
    else:
        click.echo(Fore.RED + "Either include a post code, or the --api-server flag.")


if __name__ == '__main__':
    run()
