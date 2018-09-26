from datetime import timedelta
from json import JSONDecodeError
from typing import Optional

import aiohttp
from aiobreaker import CircuitBreaker

from hyperion import logger
from hyperion.models import Postcode
from . import ApiError

# todo add pytest


postcode_breaker = CircuitBreaker(fail_max=3, timeout_duration=timedelta(hours=1))


@postcode_breaker
async def get_from_url(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as request:
                if request.status == 404:
                    return None
                else:
                    postcode_request = await request.json()
        except ConnectionError as con_err:
            logger.error(f"Could not connect to {con_err.host}")
            raise ApiError(f"Could not connect to {con_err.host}")
        except JSONDecodeError as dec_err:
            logger.error(f"Could not decode data: {dec_err}")
            raise ApiError(f"Could not decode data: {dec_err}")

    postcode = postcode_request["result"]["postcode"]
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


async def fetch_postcode_from_string(postcode: str) -> Optional[PostCode]:
    """
    Gets a postcode object from a string representation.
    :param postcode: The postcode to look up.
    :return: The mapping corresponding to that postcode or none if the postcode does not exist.
    :raises ApiError: When there was an error connecting to the API.
    :raises CircuitBreakerError: When the circuit breaker is open.
    """
    postcode_lookup = f"https://api.postcodes.io/postcodes/{postcode}"
    return await get_from_url(postcode_lookup)


async def fetch_postcodes_from_coordinates(lat: float, long: float) -> Optional[List[Postcode]]:
    """
    Gets a postcode object from the lat and long.
    :param lat: The latitude to look up.
    :param long: The longitude to look up.
    :return: The mapping corresponding to the lat and long or none if the postcode does not exist.
    :raises ApiError: When there was an error connecting to the API.
    :raises CircuitBreakerError: When the circuit breaker is open.
    """
    postcode_lookup = f"https://api.postcodes.io/postcodes?lat=:{lat}&lon=:{long}"
    return await get_from_url(postcode_lookup)


async def fetch_postcode_random() -> Postcode:
    """
    Gets a random postcode object.
    :raises ApiError: When there was an error connecting to the API.
    :raises CircuitBreakerError: When the circuit breaker is open.
    """
    postcode_lookup = f"https://api.postcodes.io/random/postcodes"
    return await get_from_url(postcode_lookup)
