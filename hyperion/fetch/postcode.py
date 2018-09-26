from datetime import timedelta
from json import JSONDecodeError
from typing import Optional, Union, List

from aiohttp import ClientSession, ClientConnectionError
from aiobreaker import CircuitBreaker

from hyperion import logger
from hyperion.models import Postcode
from . import ApiError


postcode_breaker = CircuitBreaker(fail_max=3, timeout_duration=timedelta(hours=1))
base_url = "https://api.postcodes.io"


@postcode_breaker
async def _get_postcode_from_url(path) -> Optional[Union[Postcode, List[Postcode]]]:
    def postcode_from_dict(data):
        return Postcode(
            postcode=data["postcode"],
            lat=data["latitude"],
            long=data["longitude"],
            country=data["country"],
            district=data["admin_district"],
            zone=data["msoa"]
        )

    async with ClientSession() as session:
        try:
            async with session.get(base_url + path) as request:
                if request.status == 404:
                    return None
                else:
                    postcode_request = await request.json()
        except ClientConnectionError as con_err:
            logger.debug(f"Could not connect to {con_err.host}")
            raise ApiError(f"Could not connect to {con_err.host}")
        except JSONDecodeError as dec_err:
            logger.error(f"Could not decode data: {dec_err}")
            raise ApiError(f"Could not decode data: {dec_err}")

    if isinstance(postcode_request["result"], list):
        return [postcode_from_dict(entry) for entry in postcode_request["result"]]
    else:
        return postcode_from_dict(postcode_request["result"])


async def fetch_postcode_from_string(postcode: str) -> Optional[Postcode]:
    """
    Gets a postcode object from a string representation.
    :param postcode: The postcode to look up.
    :return: The mapping corresponding to that postcode or none if the postcode does not exist.
    :raises ApiError: When there was an error connecting to the API.
    :raises CircuitBreakerError: When the circuit breaker is open.
    """
    postcode_lookup = f"/postcodes/{postcode}"
    return await _get_postcode_from_url(postcode_lookup)


async def fetch_postcodes_from_coordinates(lat: float, long: float) -> Optional[List[Postcode]]:
    """
    Gets a postcode object from the lat and long.
    :param lat: The latitude to look up.
    :param long: The longitude to look up.
    :return: The mapping corresponding to the lat and long or none if the postcode does not exist.
    :raises ApiError: When there was an error connecting to the API.
    :raises CircuitBreakerError: When the circuit breaker is open.
    """
    postcode_lookup = f"/postcodes?lat={lat}&lon={long}"
    return await _get_postcode_from_url(postcode_lookup)


async def fetch_postcode_random() -> Postcode:
    """
    Gets a random postcode object.
    :raises ApiError: When there was an error connecting to the API.
    :raises CircuitBreakerError: When the circuit breaker is open.
    """
    postcode_lookup = f"/random/postcodes"
    return await _get_postcode_from_url(postcode_lookup)
