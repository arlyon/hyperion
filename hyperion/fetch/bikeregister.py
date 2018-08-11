import json
from datetime import timedelta
from typing import List
from xml import etree

import aiohttp
from pybreaker import CircuitBreaker

from hyperion.fetch import ApiError

bike_breaker = CircuitBreaker(fail_max=3, timeout_duration=timedelta(days=3))


@bike_breaker
async def fetch_bikes() -> List[dict]:
    """
    Gets the full list of bikes from the bikeregister site.
    The data is hidden behind a form post request and so
    we need to extract an xsrf and session token with bs4.

    todo add pytest tests

    :return: All the currently registered bikes.
    :raise ApiError: When there was an error connecting to the API.
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('https://www.bikeregister.com/stolen-bikes') as request:
                soup = etree.fromstring(await request.text())
        except aiohttp.ClientConnectionError as con_err:
            logger.error(f"Could not connect to {con_err.host}")
            raise ApiError(f"Could not connect to {con_err.host}")

        token = soup.find("input", {"name": "_token"}).get('value')
        xsrf_token = request.cookies["XSRF-TOKEN"]
        laravel_session = request.cookies["laravel_session"]

        # get the bike data
        headers = {
            'cookie': f'XSRF-TOKEN={xsrf_token}; laravel_session={laravel_session}',
            'origin': 'https://www.bikeregister.com',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'accept': '*/*',
            'referer': 'https://www.bikeregister.com/stolen-bikes',
            'authority': 'www.bikeregister.com',
            'x-requested-with': 'XMLHttpRequest',
        }

        data = [
            ('_token', token),
            ('make', ''),
            ('model', ''),
            ('colour', ''),
            ('reporting_period', '1'),
        ]

        try:
            async with session.post('https://www.bikeregister.com/stolen-bikes', headers=headers, data=data) as request:
                bikes = json.loads(await request.text())
        except aiohttp.ClientConnectionError as con_err:
            logger.error(f"Could not connect to {con_err.host}")
            raise ApiError(f"Could not connect to {con_err.host}")
        except json.JSONDecodeError as dec_err:
            logger.error(f"Could not decode data: {dec_err.msg}")
            raise ApiError(f"Could not decode data: {dec_err.msg}")

        return bikes

    # if cant open a session
    return []
