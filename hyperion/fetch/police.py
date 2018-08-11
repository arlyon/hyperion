from datetime import timedelta
from json import JSONDecodeError
from typing import Optional, List, Dict

import aiohttp
from pybreaker import CircuitBreaker

from hyperion import logger
from hyperion.fetch import ApiError

police_breaker = CircuitBreaker(fail_max=3, timeout_duration=timedelta(hours=1))


@police_breaker
async def fetch_neighbourhood(lat: float, long: float) -> Optional[dict]:
    """
    Gets the neighbourhood from the fetch that is associated with the given postcode.
    :return: A neighbourhood object parsed from the fetch.
    :raise ApiError: When there was an error connecting to the API.
    """

    lookup_url = f"https://data.police.uk/fetch/locate-neighbourhood?q={lat},{long}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(lookup_url) as request:
                neighbourhood = await request.json()
        except aiohttp.ClientConnectionError as con_err:
            logger.error(f"Could not connect to {con_err.host}")
            raise ApiError(f"Could not connect to {con_err.host}")
        except JSONDecodeError as dec_err:
            logger.error(f"Could not decode data: {dec_err}")
            raise ApiError(f"Could not decode data: {dec_err}")

        neighbourhood_url = f"https://data.police.uk/fetch/{neighbourhood['force']}/{neighbourhood['neighbourhood']}"

        try:
            async with session.get(neighbourhood_url) as request:
                neighbourhood_data = await request.json()
        except ConnectionError as con_err:
            logger.error(f"Could not connect to {con_err.args[0].pool.host}")
            raise ApiError(f"Could not connect to {con_err.args[0].pool.host}")
        except JSONDecodeError as dec_err:
            logger.error(f"Could not decode data: {dec_err}")
            raise ApiError(f"Could not decode data: {dec_err}")

        return neighbourhood_data


@police_breaker
async def fetch_crime(lat: float, long: float) -> List[Dict]:
    """
    Gets crime for a given lat and long.
    :raise ApiError: When there was an error connecting to the API.

    todo cache
    """
    crime_lookup = f"https://data.police.uk/api/crimes-street/all-crime?lat={lat}&lng={long}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(crime_lookup) as request:
                crime_request = await request.json()
        except ConnectionError as con_err:
            logger.error(f"Could not connect to {con_err.args[0].pool.host}")
            raise ApiError(f"Could not connect to {con_err.args[0].pool.host}")
        except JSONDecodeError as dec_err:
            logger.error(f"Could not decode data: {dec_err}")
            raise ApiError(f"Could not decode data: {dec_err}")
        else:
            return crime_request
