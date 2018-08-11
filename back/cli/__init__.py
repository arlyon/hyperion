import json
from math import floor
from typing import Tuple, Dict

import click
import geopy.distance
from click import echo
from colorama import Fore

from back.fetch import ApiError
from back.fetch.police import fetch_crime
from back.fetch.wikipedia import fetch_nearby
from back.models import CachingError
from back.models.util import get_postcode, get_bikes


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
            echo("\n".join(f"    {bike['model']} {bike['make']}: {bike['distance']}m away" for bike in data['bikes'][:10]))
            if len(data['bikes']) > 10:
                echo(f"    {Fore.BLUE}(limited to 10){Fore.RESET}")
        if "crimes" in data:
            echo(f"  Crimes Committed: {len(data['crimes'])}")
        if "nearby" in data:
            echo("  Points of Interest:")
            for x in data["nearby"]:
                echo(f"    {x['dist']}m - {x['title']}")


async def cli(postcode_strings: Tuple[str], bikes: bool, crime: bool, nearby: bool, json: bool):
    """
    Runs the CLI app.

    :param bikes: A flag to include bikes.
    :param crime: A flag to include crime.
    :param nearby: A flag to include nearby.
    :param json: A flag to make json output.
    :param postcode_strings: The desired postcode.
    """

    postcodes = {}
    success = True

    for postcode_str in postcode_strings:
        data = {}
        try:
            postcode = await get_postcode(postcode_str)
            data["location"] = postcode.serialize()
            coordinates = geopy.Point(postcode.lat, postcode.long)
        except CachingError as e:
            echo(e)
            echo(f"Not cached: {postcode_str}")
            success = False
            continue

        if bikes:
            try:
                data["bikes"] = [bike.serialize() for bike in await get_bikes(postcode.postcode)]
                for bike in data["bikes"]:
                    bike["distance"] = floor(geopy.distance.vincenty(geopy.Point(bike['latitude'], bike['longitude']), coordinates).kilometers * 1000)
                data["bikes"] = sorted(data["bikes"], key=lambda bike: bike["distance"])
            except CachingError as e:
                success = False
                echo(e)
        if crime:
            try:
                data["crimes"] = await fetch_crime(postcode.lat, postcode.long)
            except ApiError as e:
                success = False
                echo(e)
        if nearby:
            try:
                data["nearby"] = await fetch_nearby(postcode.lat, postcode.long)
            except ApiError as e:
                success = False
                echo(e)

        postcodes[data['location']['postcode']] = data

    await (display_json(postcodes) if json else display_human(postcodes))
    return 0 if success else 1
