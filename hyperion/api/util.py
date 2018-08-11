from functools import partial
from json import dumps
from typing import Optional
import re

from aiohttp import web
from aiohttp.web import json_response, middleware

str_dumps = partial(dumps, default=str)
str_json_response = partial(json_response, dumps=str_dumps)
postcode_regex = re.compile("^([Gg][Ii][Rr] 0[Aa]{2})|"
                            "((([A-Za-z][0-9]{1,2})|"
                            "(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|"
                            "(([A-Za-z][0-9][A-Za-z])|"
                            "([A-Za-z][A-Ha-hJ-Yj-y][0-9]?[A-Za-z])))) ?"
                            "[0-9][A-Za-z]{2})$")


@middleware
async def normalize_postcode_middleware(request, handler):
    """
    If there is a postcode in the url it validates and normalizes it.
    :param request:
    :param handler:
    :return:
    """
    postcode: Optional[str] = request.match_info.get('postcode', None)

    if postcode is None or not postcode_regex.match(postcode):
        raise web.HTTPNotFound(text="Invalid Postcode")

    postcode_processed = postcode.upper().replace(" ", "")
    if postcode_processed == postcode:
        return await handler(request)
    else:
        url_name = request.match_info.route.name
        url = request.app.router[url_name]
        params = dict(request.match_info)
        params['postcode'] = postcode_processed
        raise web.HTTPFound(str(url.url_for(**params)))
