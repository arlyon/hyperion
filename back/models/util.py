import datetime
from typing import List

import geopy
import geopy.distance
from peewee import DoesNotExist

from back.api import ApiError
from back.api.bikeregister import get_new_bikes_from_api
from back.api.police import get_neighbourhood_from_api
from back.api.postcodes import get_postcode_from_api
from back.models import PostCodeMapping, Neighbourhood, db, Location, Link, Bike


def should_update_bikes():
    """
    Checks the most recently cached bike and returns true if
    it either doesn't exist or
    :return: Whether the cache should be updated.

    todo what if there are no bikes added for a week? ... every request will be triggered.
    """
    bike = Bike.get_most_recent_bike()
    if bike is not None:
        return bike.cached_date < datetime.datetime.now() - datetime.timedelta(days=7)
    else:
        return True


def get_stolen_bikes(postcode: str, kilometers=10) -> List[Bike] or None:
    """
    Gets stolen bikes from the database within a
    certain radius (km) of a given postcode. Selects
    a square from the database and then filters out
    the corners of the square.
    :param postcode: The postcode to look up.
    :param kilometers: The radius (km) of the search.
    :return: The bikes in that radius.
    """

    if should_update_bikes():
        try:
            new_bikes = get_new_bikes_from_api()
            Bike.insert_many(new_bikes).execute()
        except ApiError:
            pass

    mapping = get_postcode(postcode)

    # create point and distance
    center = geopy.Point(mapping.lat, mapping.long)
    distance = geopy.distance.vincenty(kilometers=kilometers)

    # calculate edges of a square and retrieve
    lat_end = distance.destination(point=center, bearing=0).latitude
    lat_start = distance.destination(point=center, bearing=180).latitude
    long_start = distance.destination(point=center, bearing=270).longitude
    long_end = distance.destination(point=center, bearing=90).longitude

    bikes_in_area = Bike.select().where(
        lat_start <= Bike.latitude,
        Bike.latitude <= lat_end,
        long_start <= Bike.longitude,
        Bike.longitude <= long_end
    )

    # filter out items in square that aren't within the radius and return
    return [
        bike for bike in bikes_in_area
        if geopy.distance.vincenty(geopy.Point(bike.latitude, bike.longitude), center).kilometers < kilometers
    ]


def get_postcode(postcode: str) -> PostCodeMapping or None:
    """
    Gets the postcode mapping for a given postcode.
    Acts as a middleware between us and the API, caching results.
    :param postcode: The postcode.
    :return: the Mapping.
    """
    postcode = postcode.replace(" ", "")
    try:
        return PostCodeMapping.get(PostCodeMapping.postcode == postcode)
    except DoesNotExist:
        try:
            mapping = get_postcode_from_api(postcode)
        except ApiError:
            return None

        if mapping is not None:
            mapping.save()

        return mapping


def get_neighbourhood(postcode: str) -> Neighbourhood or None:
    """
    Gets a police neighbourhood from the database.
    Acts as a middleware between us and the API, caching results.
    :param postcode: The UK postcode to look up.
    :return: The Neighbourhood or None if not found.
    """
    postcode = postcode.replace(" ", "")
    mapping = get_postcode(postcode)
    if mapping is None:
        return None
    elif mapping.neighbourhood is not None:
        return mapping.neighbourhood
    else:
        try:
            neighbourhood, locations, links = get_neighbourhood_from_api(mapping)
        except ApiError:
            return None

        if neighbourhood is not None:
            with db.atomic() as transaction:
                neighbourhood.save()
                Location.insert_many(locations)
                Link.insert_many(links)

        return neighbourhood
