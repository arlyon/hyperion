import asyncio
import logging
from datetime import timedelta, datetime
from typing import List, Optional

import geopy
import geopy.distance
from peewee import DoesNotExist
from pybreaker import CircuitBreakerError

from back.fetch import ApiError
from back.fetch.bikeregister import fetch_bikes
from back.fetch.police import fetch_neighbourhood
from back.fetch.postcode import fetch_postcode
from back.models import PostCode, Neighbourhood, db, Bike
from back.models import CachingError, PostCodeLike


async def update_bikes(delta: timedelta):
    """
    A background task that retrieves bike data.
    :param delta: The amount of time to wait between checks.
    """
    while True:
        logging.info("Fetching bike data.")
        if await should_update_bikes(delta):
            try:
                bike_data = await fetch_bikes()
            except ApiError:
                logging.error(f"Failed to fetch bikes.")
            except CircuitBreakerError:
                logging.error(f"Failed to fetch bikes (circuit breaker open).")
            else:
                # save only bikes that aren't in the db
                most_recent_bike = Bike.get_most_recent_bike()
                new_bikes = (
                    Bike.from_dict(bike) for index, bike in enumerate(bike_data)
                    if index > (most_recent_bike.id if most_recent_bike is not None else -1)
                )
                with db.atomic():
                    for bike in new_bikes:
                        bike.save()
                logging.info(f"Saved {len(new_bikes)} new entries.")
        else:
            logging.info("Bike data up to date. Sleeping.")

        await asyncio.sleep(delta.total_seconds())


async def should_update_bikes(delta: timedelta):
    """
    Checks the most recently cached bike and returns true if
    it either doesn't exist or
    :return: Whether the cache should be updated.

    todo what if there are no bikes added for a week? ... every request will be triggered.
    """
    bike = Bike.get_most_recent_bike()
    if bike is not None:
        return bike.cached_date < datetime.now() - delta
    else:
        return True


async def get_bikes(postcode: PostCodeLike, kilometers=10) -> Optional[List[Bike]]:
    """
    Gets stolen bikes from the database within a
    certain radius (km) of a given postcode. Selects
    a square from the database and then filters out
    the corners of the square.
    :param postcode: The postcode to look up.
    :param kilometers: The radius (km) of the search.
    :return: The bikes in that radius or None if the postcode doesn't exist.
    """

    try:
        postcode = await get_postcode(postcode)
    except CachingError as e:
        raise e

    if postcode is None:
        return None

    # create point and distance
    center = geopy.Point(postcode.lat, postcode.long)
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


async def get_postcode(postcode: PostCodeLike) -> Optional[PostCode]:
    """
    Gets the postcode object for a given postcode string.
    Acts as a middleware between us and the API, caching results.
    :param postcode: The either a string postcode or PostCode object.
    :return: The PostCode object else None if the postcode does not exist..
    :raises CachingError: When the postcode is not in cache, and the API is unreachable.
    """
    if isinstance(postcode, PostCode):
        return postcode

    postcode = postcode.replace(" ", "").upper()

    try:
        postcode = PostCode.get(PostCode.postcode == postcode)
    except DoesNotExist:
        try:
            postcode = await fetch_postcode(postcode)
        except (ApiError, CircuitBreakerError):
            raise CachingError(f"Requested postcode is not cached, and we could not get any information about it.")
        if postcode is not None:
            postcode.save()
    else:
        return postcode


async def get_neighbourhood(postcode: PostCodeLike) -> Optional[Neighbourhood]:
    """
    Gets a police neighbourhood from the database.
    Acts as a middleware between us and the API, caching results.
    :param postcode: The UK postcode to look up.
    :return: The Neighbourhood or None if the postcode does not exist.
    :raises CachingError: If the needed neighbourhood is not in cache, and the fetch isn't responding.

    todo save locations/links
    """
    try:
        postcode = await get_postcode(postcode)
    except CachingError as e:
        raise e
    else:
        if postcode is None:
            return None
        elif postcode.neighbourhood is not None:
            return postcode.neighbourhood

    try:
        data = await fetch_neighbourhood(postcode.lat, postcode.long)
    except ApiError as e:
        raise CachingError(f"Neighbourhood not in cache, and could not reach API: {e.status}")

    if data is not None:
        neighbourhood = Neighbourhood.from_dict(data)

        with db.atomic():
            neighbourhood.save()
            postcode.neighbourhood = neighbourhood
            postcode.save()
            for location in locations:
                location.save()
            for link in links:
                link.save()

    return neighbourhood
