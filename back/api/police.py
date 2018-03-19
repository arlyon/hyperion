import json
import logging
from typing import Tuple, List

import requests

from back.api import ApiError
from back.models import Neighbourhood, Link, Location, PostCodeMapping


def get_neighbourhood_from_api(mapping: PostCodeMapping) -> Tuple[Neighbourhood or None, List[Location] or None, List[Link] or None]:
    """
    Gets the neighbourhood from the api that is associated with the given postcode.
    :param mapping: A postcode object.
    :return: A neighbourhood object parsed from the api.
    :raise ApiError: When there was an error connecting to the API.
    """
    locate_url = f"https://data.police.uk/api/locate-neighbourhood?q={mapping.lat},{mapping.long}"

    try:
        neighbourhood = requests.get(locate_url).json()
    except requests.exceptions.ConnectionError as con_err:
        logging.error(f"Could not connect to {con_err.args[0].pool.host}")
        raise ApiError(f"Could not connect to {con_err.args[0].pool.host}")
    except json.JSONDecodeError:
        # the neighbourhood is not in the police database
        return None, None, None

    neighbourhood_lookup_url = f"https://data.police.uk/api/{neighbourhood['force']}/{neighbourhood['neighbourhood']}"

    try:
        neighbourhood_data = requests.get(neighbourhood_lookup_url).json()  # get the json and parse it immediately
    except requests.exceptions.ConnectionError as con_err:
        logging.error(f"Could not connect to {con_err.args[0].pool.host}")
        raise ApiError(f"Could not connect to {con_err.args[0].pool.host}")
    except json.JSONDecodeError as dec_err:
        logging.error(f"Could not decode data: {dec_err}")
        raise ApiError(f"Could not decode data: {dec_err}")

    neighbourhood = Neighbourhood(
        code=neighbourhood_data["id"],
        email=neighbourhood_data["contact_details"]["email"] if "email" in neighbourhood_data[
            "contact_details"] else None,
        facebook=neighbourhood_data["contact_details"]["facebook"] if "facebook" in neighbourhood_data[
            "contact_details"] else None,
        telephone=neighbourhood_data["contact_details"]["telephone"] if "telephone" in neighbourhood_data[
            "contact_details"] else None,
        twitter=neighbourhood_data["contact_details"]["twitter"] if "twitter" in neighbourhood_data[
            "contact_details"] else None,
        name=neighbourhood_data["name"],
        description=neighbourhood_data["description"] if "description" in neighbourhood_data else None
    )

    links = [
        Link(
            name=link["title"],
            url=link["url"],
            neighbourhood=neighbourhood,
        )
        for link in neighbourhood_data["links"]
    ]

    locations = [
        Location(
            address=location["address"],
            description=location["description"],
            latitude=location["latitude"],
            longitude=location["longitude"],
            name=location["name"],
            neighbourhood=neighbourhood,
            postcode=mapping,
            type=location["type"],
        )
        for location in neighbourhood_data["locations"]
    ]

    return neighbourhood, locations, links
