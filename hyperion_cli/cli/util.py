from dataclasses import dataclass, field
from typing import List, Dict, Optional

from geopy import Point

from ..fetch import ApiError
from ..fetch.police import fetch_crime
from ..fetch.wikipedia import fetch_nearby
from ..models import Postcode, Bike, CachingError
from ..models.util import get_bikes


@dataclass
class PostcodeData:
    postcode: Postcode
    bikes: Optional[List[Bike]] = field(default=None)
    crime: Optional[List[Dict]] = field(default=None)
    nearby: Optional[List[Dict]] = field(default=None)


async def get_postcode_data(postcode, bikes, crime, nearby):
    exceptions = []
    coordinates = Point(postcode.lat, postcode.long)

    bikes_list = None
    crime_list = None
    nearby_list = None

    if bikes:
        try:
            bikes_list = await get_bikes(postcode.postcode)
        except CachingError:
            exceptions.append(f"could not get bikes for {postcode.postcode}")

    if crime:
        try:
            crime_list = await fetch_crime(coordinates.latitude, coordinates.longitude)
        except ApiError:
            exceptions.append(f"could not get crimes for {postcode.postcode}")

    if nearby:
        try:
            nearby_list = await fetch_nearby(coordinates.latitude, coordinates.longitude)
        except ApiError:
            exceptions.append(f"could not get nearby for {postcode.postcode}")

    return PostcodeData(
        postcode,
        bikes_list,
        crime_list,
        nearby_list
    ), exceptions
