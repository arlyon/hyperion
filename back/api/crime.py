from typing import Optional

from aiohttp import web
from pybreaker import CircuitBreakerError

from back.fetch import ApiError
from back.fetch.police import fetch_crime
from back.models import PostCode, CachingError
from .util import str_json_response
from back.models.util import get_postcode, get_neighbourhood


async def api_crime(request):
    """
    Gets the crime nearby to a given postcode.
    :param request: The aiohttp request.
    :return: A json representation of the crimes near the postcode.
    """
    postcode: Optional[str] = request.match_info.get('postcode', None)

    try:
        postcode: Optional[PostCode] = await get_postcode(postcode)
    except CachingError as e:
        return web.Response(body=e.status, status=500)

    try:
        crime = await fetch_crime(postcode.lat, postcode.long)
    except (ApiError, CircuitBreakerError):
        raise web.HTTPInternalServerError(body=f"Requested crime is not cached, and we could not find any information about it.")

    if crime is None:
        return web.HTTPNotFound(body="No Police Data")
    else:
        return str_json_response(crime)


async def api_neighbourhood(request):
    """
    Gets police data about a neighbourhood.
    :param request: The aiohttp request.
    :return: The police data for that post code.
    """
    postcode: Optional[str] = request.match_info.get('postcode', None)

    try:
        neighbourhood = await get_neighbourhood(postcode)
    except CachingError as e:
        return web.Response(body=e.status, status=500)

    if neighbourhood is None:
        return web.Response(body="No Police Data", status=404)
    else:
        return str_json_response(neighbourhood.serialize())
