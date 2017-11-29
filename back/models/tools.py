from json import JSONDecodeError

import datetime
from typing import List

import geopy
import geopy.distance
import requests
from bs4 import BeautifulSoup
from peewee import DoesNotExist

from back.models.location import Location
from back.models.neighbourhood import Neighbourhood, Link
from back.models.postcode import PostCodeMapping
from back.models.bikes import Bike


def get_postcode_mapping(postcode: str) -> PostCodeMapping or None:
    """w
    Gets the postcode mapping for a given postcode.
    Acts as a middleware between us and the API, caching results.
    :param postcode: The postcode.
    :return: the Mapping.
    """
    postcode = postcode.replace(" ", "")
    try:
        return PostCodeMapping.get(PostCodeMapping.postcode == postcode)
    except DoesNotExist:
        postcode_lookup = f"https://api.postcodes.io/postcodes/{postcode}"
        postcode_request = requests.get(postcode_lookup).json()

        if postcode_request["status"] == 404:
            return None

        lat = round(postcode_request["result"]["latitude"], 6)
        long = round(postcode_request["result"]["longitude"], 6)
        country = postcode_request["result"]["country"]
        district = postcode_request["result"]["admin_district"]
        zone = postcode_request["result"]["msoa"]

        return PostCodeMapping.create(
            postcode=postcode,
            lat=lat,
            long=long,
            country=country,
            district=district,
            zone=zone
        )  # the peewee function for creating new entities


def get_neighbourhood_from_db(postcode: str) -> Neighbourhood or None:
    """
    Gets a police neighbourhood from the database.
    Acts as a middleware between us and the API, caching results.
    :param postcode: The postcode to look up.
    :return: The Neighbourhood or None if not found.
    """
    postcode = postcode.replace(" ", "")
    mapping = get_postcode_mapping(postcode)
    if mapping is None:
        return None
    elif mapping.neighbourhood is not None:
        return mapping.neighbourhood
    else:
        neighbourhood_find_url = f"https://data.police.uk/api/locate-neighbourhood?q={mapping.lat},{mapping.long}"

        try:
            neighbourhood_name = requests.get(neighbourhood_find_url).json()  # get the json and parse it immediately
        except JSONDecodeError:
            # the neighbourhood is not in the police database
            return None

        neighbourhood_lookup_url = f"https://data.police.uk/api/{neighbourhood_name['force']}/{neighbourhood_name['neighbourhood']}"
        neighbourhood_data = requests.get(neighbourhood_lookup_url).json()  # get the json and parse it immediately

        neighbourhood = Neighbourhood.create(
            code=neighbourhood_data["id"],
            email=neighbourhood_data["contact_details"]["email"] if "email" in neighbourhood_data[
                "contact_details"] else None,
            facebook=neighbourhood_data["contact_details"]["facebook"] if "facebook" in neighbourhood_data[
                "contact_details"] else None,
            telephone=neighbourhood_data["contact_details"]["telephone"] if "telephone" in neighbourhood_data[
                "contact_details"] else None,
            twitter=neighbourhood_data["contact_details"]["twitter"] if "twitter" in neighbourhood_data[
                "contact_details"] else None,
            name=neighbourhood_data["name"],
            description=neighbourhood_data["description"] if "description" in neighbourhood_data else None
        )

        for link in neighbourhood_data["links"]:
            Link.create(
                name=link["title"],
                url=link["url"],
                neighbourhood=neighbourhood,
            )

        for location in neighbourhood_data["locations"]:
            Location.create(
                address=location["address"],
                description=location["description"],
                latitude=location["latitude"],
                longitude=location["longitude"],
                name=location["name"],
                neighbourhood=neighbourhood,
                postcode=mapping,
                type=location["type"],
            )

        mapping.neighbourhood = neighbourhood
        mapping.save()

        return neighbourhood


def should_update_bikes():
    bike = most_recent_bike()
    if bike is not None:
        return bike.cached_date < datetime.datetime.now()-datetime.timedelta(days=1)
    else:
        return True


def most_recent_bike() -> Bike or None:
    try:
        return Bike.select().order_by(Bike.cached_date.desc()).get()
    except DoesNotExist:
        return None


def get_bikes_from_db(postcode: str, radius=10) -> List[Bike] or None:

    if should_update_bikes():
        get_and_cache_from_server()

    mapping = get_postcode_mapping(postcode)

    start = geopy.Point(mapping.lat, mapping.long)
    distance = geopy.distance.vincenty(kilometers=radius * 1.6)

    lat_end = distance.destination(point=start, bearing=0).latitude
    lat_start = distance.destination(point=start, bearing=180).latitude
    long_start = distance.destination(point=start, bearing=270).longitude
    long_end = distance.destination(point=start, bearing=90).longitude

    return Bike.select().where(
        lat_start < Bike.latitude,
        Bike.latitude < lat_end,
        long_start < Bike.longitude,
        Bike.longitude < long_end
    )


def get_and_cache_from_server():
    """
    Gets the full list of bikes from the bikeregister site.
    :return:
    """
    session = requests.session()
    request = session.get('https://www.bikeregister.com/stolen-bikes')
    soup = BeautifulSoup(request.text, 'html.parser')

    token = soup.find("input", {"name": "_token"}).get('value')
    xsrf_token = request.cookies["XSRF-TOKEN"]
    laravel_session = request.cookies["laravel_session"]

    # __cfduid, cart_identifier, locale, XSRF-TOKEN, laravel_session
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

    request = requests.post('https://www.bikeregister.com/stolen-bikes', headers=headers, data=data)
    data = request.json()

    most_recent_cache = most_recent_bike()

    cached_id = most_recent_cache.id if most_recent_cache is not None else -1

    for index, line in enumerate(data):
        if index > cached_id:
            Bike.create(
                id=index,
                make=line["make"],
                model=line["model"],
                colour=line["colour"],
                latitude=line["latitude"] if not line["latitude"] == "" else None,
                longitude=line["longitude"] if not line["longitude"] == "" else None,
                frame_number=line["frame_number"],
                rfid=line["rfid"],
                description=line["description"],
                reported_at=line["reported_at"]
            )

    return data
