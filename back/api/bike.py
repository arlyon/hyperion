from typing import Optional

from aiohttp import web

from back.models.util import get_bikes
from back.models import CachingError
from back.api.util import str_json_response


async def api_bikes(request):
    """
    Gets stolen bikes within a radius of a given postcode.
    :param request: The aiohttp request.
    :return: The bikes stolen with the given range from a postcode.
    """
    postcode: Optional[str] = request.match_info.get('postcode', None)

    try:
        radius = int(request.match_info.get('radius', 10))
    except ValueError:
        raise web.HTTPBadRequest(body="Invalid radius.")

    try:
        bikes = await get_bikes(postcode, radius)
    except CachingError as e:
        return web.HTTPInternalServerError(text=e.status)
    else:
        if bikes is None:
            return web.HTTPNotFound(text="Post code does not exist.")
        else:
            return str_json_response([bike.serialize() for bike in bikes])
