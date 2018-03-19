import json
import logging
from typing import List

import brotli
import requests
from bs4 import BeautifulSoup

from api import ApiError
from models import Bike


def get_new_bikes_from_api() -> List[Bike]:
    """
    Gets the full list of bikes from the bikeregister site.
    The data is hidden behind a form post request and so
    we need to extract an xsrf and session token with bs4.
    :return: The new bikes from the api.
    :raise ApiError: When there was an error connecting to the API.
    """

    # get the required auth tokens
    session = requests.session()

    try:
        request = session.get('https://www.bikeregister.com/stolen-bikes')
    except requests.exceptions.ConnectionError as con_err:
        logging.error(f"Could not connect to {con_err.args[0].pool.host}")
        raise ApiError(f"Could not connect to {con_err.args[0].pool.host}")

    soup = BeautifulSoup(request.text, 'html.parser')

    token = soup.find("input", {"name": "_token"}).get('value')
    xsrf_token = request.cookies["XSRF-TOKEN"]
    laravel_session = request.cookies["laravel_session"]

    # get the bike data
    headers = {
        'cookie': f'XSRF-TOKEN={xsrf_token}; laravel_session={laravel_session}',
        'origin': 'https://www.bikeregister.com',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
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
        request = requests.post('https://www.bikeregister.com/stolen-bikes', headers=headers, data=data)
        data = json.loads(brotli.decompress(request.content))  # data is compressed with brotli
    except requests.exceptions.ConnectionError as con_err:
        logging.error(f"Could not connect to {con_err.args[0].pool.host}")
        raise ApiError(f"Could not connect to {con_err.args[0].pool.host}")
    except brotli.Error as brot_err:
        logging.error(f"Could not decompress data: {brot_err}")
        raise ApiError(f"Could not decompress data: {brot_err}")
    except json.JSONDecodeError as dec_err:
        logging.error(f"Could not decode data: {dec_err}")
        raise ApiError(f"Could not decode data: {dec_err}")

    # return bikes that aren't in the db
    most_recent_bike = Bike.get_most_recent_bike()

    new_bikes = [
        Bike(
            id=index,
            make=bike["make"],
            model=bike["model"],
            colour=bike["colour"],
            latitude=bike["latitude"] if not bike["latitude"] == "" else None,
            longitude=bike["longitude"] if not bike["longitude"] == "" else None,
            frame_number=bike["frame_number"],
            rfid=bike["rfid"],
            description=bike["description"],
            reported_at=bike["reported_at"])
        for index, bike in enumerate(data)
        if index > (most_recent_bike.id if most_recent_bike is not None else -1)
    ]

    return new_bikes
