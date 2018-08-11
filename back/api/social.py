from aiohttp import web

from back.fetch import ApiError
from back.fetch.twitter import fetch_twitter
from .util import str_json_response


async def api_twitter(request):
    """
    Gets the twitter feed from a given handle.
    :return: The feed in json format.
    """
    handle = request.match_info.get('handle', None)
    if handle is None:
        return web.Response(body="Not found.", status=404)

    try:
        posts = await fetch_twitter(handle)
    except ApiError as e:
        return web.Response(body=e.status, status=500)
    return str_json_response(posts)
