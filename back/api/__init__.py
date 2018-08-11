from datetime import timedelta

from aiohttp import web
from aiohttp.web_middlewares import normalize_path_middleware

import asyncio
import uvloop

from .util import normalize_postcode_middleware
from .bike import api_bikes
from .crime import api_crime, api_neighbourhood
from .geo import api_postcode, api_nearby
from .social import api_twitter
from back.models.util import update_bikes


async def start_background_tasks(app):
    app['bike_fetcher'] = app.loop.create_task(update_bikes(timedelta(days=1)))


async def cleanup_background_tasks(app):
    app['bike_fetcher'].cancel()
    await app['bike_fetcher']


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
app = web.Application(middlewares=[normalize_postcode_middleware, normalize_path_middleware()])

app.on_startup.append(start_background_tasks)
app.on_cleanup.append(cleanup_background_tasks)

app.add_routes([
    web.get('/api/postcode/{postcode}/', api_postcode, name='postcode'),
    web.get('/api/postcode/{postcode}/bikes/', api_bikes, name='bikes'),
    web.get('/api/postcode/{postcode}/bikes/{radius}/', api_bikes, name='bikes-radius'),
    web.get('/api/postcode/{postcode}/crime/', api_crime, name='crime'),
    web.get('/api/postcode/{postcode}/neighbourhood/', api_neighbourhood, name='neighbourhood'),
    web.get('/api/postcode/{postcode}/nearby/', api_nearby, name='nearby'),
    web.get('/api/postcode/{postcode}/nearby/{limit}/', api_nearby, name='nearby-radius'),
    web.get('/api/twitter/{handle}/', api_twitter, name='twitter'),
])
