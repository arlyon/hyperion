from typing import Optional

from aiohttp import web
from pybreaker import CircuitBreakerError

from back.fetch import ApiError
from back.fetch.wikipedia import fetch_nearby
from back.models import PostCode, CachingError
from .util import str_json_response
from back.models.util import get_postcode


async def api_postcode(request):
    """
    Gets data from a postcode.
    :param request: The aiohttp request.
    """
    postcode: Optional[str] = request.match_info.get('postcode', None)

    try:
        postcode: Optional[PostCode] = await get_postcode(postcode)
    except CachingError as e:
        return web.HTTPInternalServerError(body=e.status)
    except CircuitBreakerError as e:
        pass
    else:
        if postcode is not None:
            return str_json_response(postcode.serialize())
        else:
            return web.HTTPNotFound(body="Invalid Postcode")


async def api_nearby(request):
    """
    Gets wikipedia articles near a given postcode.
    :param request: The aiohttp request.
    """
    postcode: Optional[str] = request.match_info.get('postcode', None)

    try:
        limit = int(request.match_info.get('limit', 10))
    except ValueError:
        return web.HTTPBadRequest(body="Invalid limit.")

    try:
        postcode: Optional[PostCode] = await get_postcode(postcode)
    except CachingError as e:
        return web.HTTPInternalServerError(body=e.status)

    if postcode is None:
        return web.HTTPNotFound(body="Invalid Postcode")

    try:
        nearby_items = await fetch_nearby(postcode.lat, postcode.long, limit)
    except ApiError as e:
        return web.HTTPInternalServerError(body=f"No nearby locations cached, and we could not find any information about it.")

    if nearby_items is None:
        return web.HTTPNotFound(body="No Results")
    else:
        return str_json_response(nearby_items)
