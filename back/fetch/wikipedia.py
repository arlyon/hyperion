from typing import Dict, List, Optional

import requests
from requests.exceptions import ConnectionError
from pybreaker import CircuitBreaker

# todo decide parameters
from back.fetch import ApiError

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

    try:
        request = requests.get(request_url)
    except ConnectionError as con_err:
        raise ApiError(f"Could not connect to {con_err.args[0].pool.host}")

    if request.status_code == 404:
        return None

    try:
        data = request.json()["query"]["geosearch"]
    except KeyError:
        return None
    else:
        for location in data:
            location.pop("ns")
            location.pop("primary")
        return data
