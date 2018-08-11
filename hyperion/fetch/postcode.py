from datetime import timedelta
from json import JSONDecodeError
from typing import Optional

import aiohttp
from pybreaker import CircuitBreaker

from hyperion import logger
from hyperion.fetch import ApiError
from hyperion.models import PostCode

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
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(postcode_lookup) as request:
                postcode_request = await request.json()
        except ConnectionError as con_err:
            logger.error(f"Could not connect to {con_err.host}")
            raise ApiError(f"Could not connect to {con_err.host}")
        except JSONDecodeError as dec_err:
            logger.error(f"Could not decode data: {dec_err}")
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
