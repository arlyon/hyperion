from aiohttp import web

from ..fetch import ApiError
from ..fetch.twitter import fetch_twitter
from .util import str_json_response


async def api_twitter(request):
    """
    Gets the twitter feed from a given handle.
    :return: The feed in json format.
    """
    handle = request.match_info.get('handle', None)
    if handle is None:
        raise web.HTTPNotFound(body="Not found.")

    try:
        posts = await fetch_twitter(handle)
    except ApiError as e:
        raise web.HTTPInternalServerError(body=e.status)
    return str_json_response(posts.to_dict())
