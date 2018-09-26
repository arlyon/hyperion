from typing import Optional

from aiohttp import web
from pybreaker import CircuitBreakerError

from hyperion.fetch import ApiError
from hyperion.fetch.police import fetch_crime
from hyperion.models import Postcode, CachingError
from hyperion.models.util import get_postcode, get_neighbourhood, get_postcode_random
from .util import str_json_response


async def api_crime(request):
    """
    Gets the crime nearby to a given postcode.
    :param request: The aiohttp request.
    :return: A json representation of the crimes near the postcode.
    """
    postcode: Optional[str] = request.match_info.get('postcode', None)

    try:
        coroutine = get_postcode_random() if postcode == "random" else get_postcode(postcode)
        postcode: Optional[Postcode] = await coroutine
    except CachingError as e:
        return web.Response(body=e.status, status=500)

    try:
        crime = await fetch_crime(postcode.lat, postcode.long)
    except (ApiError, CircuitBreakerError):
        raise web.HTTPInternalServerError(body=f"Requested crime is not cached, and can't be retrieved.")

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
        postcode = (await get_postcode_random()) if postcode == "random" else postcode
        neighbourhood = await get_neighbourhood(postcode)
    except CachingError as e:
        raise web.HTTPInternalServerError(text=e.status)

    if neighbourhood is None:
        raise web.HTTPNotFound(text="No Police Data")
    else:
        return str_json_response(neighbourhood.serialize())
