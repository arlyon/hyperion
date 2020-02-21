"""
The api package handles the web app and all the endpoints in the hyperion http server.
"""
from asyncio import CancelledError
from datetime import timedelta

from aiohttp import web
from aiohttp.web_middlewares import normalize_path_middleware

from ..models.util import update_bikes
from .bike import api_bikes
from .crime import api_crime, api_neighbourhood
from .geo import api_postcode, api_nearby
from .social import api_twitter
from .util import normalize_postcode_middleware, enable_cross_origin
from ..settings import SERVER_HOST, SERVER_PORT


async def start_background_tasks(app):
    app['bike_fetcher'] = app.loop.create_task(update_bikes(timedelta(days=1)))


async def cleanup_background_tasks(app):
    app['bike_fetcher'].cancel()
    await app['bike_fetcher']


app = web.Application(middlewares=[normalize_path_middleware(), normalize_postcode_middleware])

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


def run_api_server(host=SERVER_HOST, port=SERVER_PORT, should_enable_cross_origin=True):
    if should_enable_cross_origin:
        enable_cross_origin(app)

    try:
        web.run_app(app, host=host, port=port)
    except CancelledError as e:
        if e.__context__ is not None:
            print(f"Could not bind to address {host}:{port}" if e.__context__.errno == 48 else e.__context__)
            exit(1)
        else:
            print("Exiting")
