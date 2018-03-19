import logging
from json import JSONDecodeError

import requests

from api import ApiError
from models import PostCodeMapping


def get_postcode_from_api(postcode: str) -> PostCodeMapping or None:
    """
    Gets a postcode from the api
    :param postcode: The postcode to look up.
    :return: The mapping corresponding to that postcode.
    :raise ApiError: When there was an error connecting to the API.
    """
    postcode_lookup = f"https://api.postcodes.io/postcodes/{postcode}"

    try:
        postcode_request = requests.get(postcode_lookup).json()
    except requests.exceptions.ConnectionError as con_err:
        logging.error(f"Could not connect to {con_err.args[0].pool.host}")
        raise ApiError(f"Could not connect to {con_err.args[0].pool.host}")
    except JSONDecodeError as dec_err:
        logging.error(f"Could not decode data: {dec_err}")
        raise ApiError(f"Could not decode data: {dec_err}")

    if postcode_request["status"] == 404:
        return None

    lat = round(postcode_request["result"]["latitude"], 6)
    long = round(postcode_request["result"]["longitude"], 6)
    country = postcode_request["result"]["country"]
    district = postcode_request["result"]["admin_district"]
    zone = postcode_request["result"]["msoa"]

    return PostCodeMapping(
        postcode=postcode,
        lat=lat,
        long=long,
        country=country,
        district=district,
        zone=zone
    )
