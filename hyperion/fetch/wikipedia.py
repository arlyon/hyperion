import logging
from json import JSONDecodeError
from typing import Dict, List, Optional

import aiohttp
from pybreaker import CircuitBreaker

from hyperion import logger
from hyperion.fetch import ApiError


wikipedia_breaker = CircuitBreaker()


@wikipedia_breaker
async def fetch_nearby(lat: float, long: float, limit: int = 10) -> Optional[List[Dict]]:
    """
    Gets wikipedia articles near a given set of coordinates.
    :raise ApiError: When there was an error connecting to the API.

    todo cache
    """
    request_url = f"https://en.wikipedia.org/w/api.php?action=query" \
                  f"&list=geosearch" \
                  f"&gscoord={lat}%7C{long}" \
                  f"&gsradius=10000" \
                  f"&gslimit={limit}" \
                  f"&format=json"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(request_url) as request:
                if request.status == 404:
                    return None
                data = (await request.json())["query"]["geosearch"]

        except ConnectionError as con_err:
            raise ApiError(f"Could not connect to {con_err.host}")
        except JSONDecodeError as dec_err:
            logger.error(f"Could not decode data: {dec_err}")
            raise ApiError(f"Could not decode data: {dec_err}")
        except KeyError:
            return None
        else:
            for location in data:
                location.pop("ns")
                location.pop("primary")
            return data
