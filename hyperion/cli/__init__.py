import json
from math import floor
from typing import Tuple, Dict

import geopy.distance
from click import echo
from colorama import Fore
from geopy import Point
from geopy.distance import vincenty

from hyperion import logger
from hyperion.fetch import ApiError
from hyperion.fetch.police import fetch_crime
from hyperion.fetch.wikipedia import fetch_nearby
from hyperion.models import CachingError
from hyperion.models.util import get_postcode, get_bikes, get_postcode_random


async def display_json(postcodes: Dict[str, Dict]):
    """
    Outputs the data for the given postcodes in json format.
    """
    echo(json.dumps(postcodes))


async def display_human(postcodes: Dict[str, Dict]):
    """
    Outputs the data for the given postcodes in a human-readable format.
    """
    for data in postcodes.values():
        echo(f"Data for: {Fore.GREEN}{data['location']['postcode']}{Fore.RESET}")
        echo(f"  Coordinates: {data['location']['lat']}, {data['location']['long']}")
        echo(f"  Zone: {data['location']['zone']}")
        echo(f"  District: {data['location']['district']}")
        echo(f"  Country: {data['location']['country']}")

        if "bikes" in data:
            echo(f"  Stolen Bikes: {Fore.GREEN}{len(data['bikes'])}{Fore.RESET}")
            echo("\n".join(
                f"    {bike['model']} {bike['make']}: {bike['distance']}m away" for bike in data['bikes'][:10]))
            if len(data['bikes']) > 10:
                echo(f"    {Fore.BLUE}(limited to 10){Fore.RESET}")
        if "crimes" in data:
            echo(f"  Crimes Committed: {len(data['crimes'])}")
        if "nearby" in data:
            echo("  Points of Interest:")
            for x in data["nearby"]:
                echo(f"    {x['dist']}m - {x['title']}")


async def cli(postcode_strings: Tuple[str], random_postcodes: int, bikes: bool, crime: bool, nearby: bool,
              as_json: bool):
    """
    Runs the CLI app.
    Tries to execute as many steps as possible to give the user
    the best understanding of the errors (if there are any).

    :param postcode_strings: A list of desired postcodes.
    :param random_postcodes: A number of random postcodes.
    :param bikes: A flag to include bikes.
    :param crime: A flag to include crime.
    :param nearby: A flag to include nearby.
    :param as_json: A flag to make json output.
    """
    postcode_data = {}
    postcode_coroutines = [(postcode, get_postcode(postcode)) for postcode in postcode_strings] + \
                          [(None, get_postcode_random()) for _ in range(random_postcodes)]

    for string, coroutine in postcode_coroutines:
        try:
            postcode = await coroutine
        except CachingError:
            postcode = None

        if postcode is None:
            logger.error("Could not get postcode" + ("." if string is None else f' "{string}"'))
        else:
            postcode_data[postcode.postcode] = postcode

    if len(postcode_data) != len(postcode_strings) + random_postcodes:
        return 1

    success = True
    for string, postcode in postcode_data.items():
        data = {"location": postcode.serialize()}
        coordinates = geopy.Point(postcode.lat, postcode.long)

        if bikes:
            try:
                data["bikes"] = [bike.serialize() for bike in await get_bikes(postcode.postcode)]
            except CachingError as e:
                success = False
                echo(e)
            else:
                for bike in data["bikes"]:
                    point = Point(bike['latitude'], bike['longitude'])
                    bike["distance"] = floor(vincenty(point, coordinates).kilometers * 1000)
                data["bikes"] = sorted(data["bikes"], key=lambda bike: bike["distance"])

        if crime:
            try:
                data["crimes"] = await fetch_crime(coordinates.latitude, coordinates.longitude)
            except ApiError as e:
                success = False
                echo(e)

        if nearby:
            try:
                data["nearby"] = await fetch_nearby(coordinates.latitude, coordinates.longitude)
            except ApiError as e:
                success = False
                echo(e)

        postcode_data[string] = data

    if success:
        await (display_json(postcode_data) if as_json else display_human(postcode_data))
        return 0
    else:
        return 1
