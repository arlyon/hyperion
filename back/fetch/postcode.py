import logging
from datetime import timedelta
from json import JSONDecodeError
from typing import Optional

import requests
from pybreaker import CircuitBreaker
from requests.exceptions import ConnectionError

from back.fetch import ApiError
from back.models import PostCode


# todo add pytest

postcode_breaker = CircuitBreaker(fail_max=3, timeout_duration=timedelta(hours=1))


@postcode_breaker
async def fetch_postcode(postcode: str) -> Optional[PostCode]:
    """
    Gets a postcode from the fetch.
    :param postcode: The postcode to look up.
    :return: The mapping corresponding to that postcode or none if the postcode does not exist.
    :raise ApiError: When there was an error connecting to the API.
    """
    postcode_lookup = f"https://api.postcodes.io/postcodes/{postcode}"

    try:
        postcode_request = requests.get(postcode_lookup).json()
    except ConnectionError as con_err:
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

    return PostCode(
        postcode=postcode,
        lat=lat,
        long=long,
        country=country,
        district=district,
        zone=zone
    )
