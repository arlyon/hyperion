import logging
from datetime import timedelta
from json import JSONDecodeError
from typing import Optional, List, Dict

import requests
from pybreaker import CircuitBreaker

from back.fetch import ApiError

from requests.exceptions import ConnectionError

police_breaker = CircuitBreaker(fail_max=3, timeout_duration=timedelta(hours=1))


@police_breaker
async def fetch_neighbourhood(lat: float, long: float) -> Optional[dict]:
    """
    Gets the neighbourhood from the fetch that is associated with the given postcode.
    :return: A neighbourhood object parsed from the fetch.
    :raise ApiError: When there was an error connecting to the API.
    """

    lookup_url = f"https://data.police.uk/fetch/locate-neighbourhood?q={lat},{long}"

    try:
        neighbourhood = requests.get(lookup_url).json()
    except ConnectionError as con_err:
        logging.error(f"Could not connect to {con_err.args[0].pool.host}")
        raise ApiError(f"Could not connect to {con_err.args[0].pool.host}")
    except JSONDecodeError:
        # the neighbourhood is not in the police database
        return None

    neighbourhood_url = f"https://data.police.uk/fetch/{neighbourhood['force']}/{neighbourhood['neighbourhood']}"

    try:
        neighbourhood_data = requests.get(neighbourhood_url).json()  # get the json and parse it immediately
    except ConnectionError as con_err:
        logging.error(f"Could not connect to {con_err.args[0].pool.host}")
        raise ApiError(f"Could not connect to {con_err.args[0].pool.host}")
    except JSONDecodeError as dec_err:
        logging.error(f"Could not decode data: {dec_err}")
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
    try:
        crime_request = requests.get(crime_lookup).json()
    except ConnectionError as con_err:
        logging.error(f"Could not connect to {con_err.args[0].pool.host}")
        raise ApiError(f"Could not connect to {con_err.args[0].pool.host}")
    except JSONDecodeError as dec_err:
        logging.error(f"Could not decode data: {dec_err}")
        raise ApiError(f"Could not decode data: {dec_err}")

    return crime_request
