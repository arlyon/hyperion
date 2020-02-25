from functools import partial
from json import dumps
from typing import Optional

import aiohttp_cors as aiohttp_cors
from aiohttp import web
from aiohttp.web import json_response, middleware

from ..util import is_uk_postcode

str_dumps = partial(dumps, default=str)
str_json_response = partial(json_response, dumps=str_dumps)


@middleware
async def normalize_postcode_middleware(request, handler):
    """
    If there is a postcode in the url it validates and normalizes it.
    """
    postcode: Optional[str] = request.match_info.get('postcode', None)

    if postcode is None or postcode == "random":
        return await handler(request)
    elif not is_uk_postcode(postcode):
        raise web.HTTPNotFound(text="Invalid Postcode")

    postcode_processed = postcode.upper().replace(" ", "")
    if postcode_processed == postcode:
        return await handler(request)
    else:
        url_name = request.match_info.route.name
        url = request.app.router[url_name]
        params = dict(request.match_info)
        params['postcode'] = postcode_processed
        raise web.HTTPMovedPermanently(str(url.url_for(**params)))


def enable_cross_origin(app):
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })
    for route in app.router.routes():
        cors.add(route)
