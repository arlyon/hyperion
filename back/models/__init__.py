from typing import Union

from peewee import SqliteDatabase

from back.fetch import ApiError

db = SqliteDatabase('data.db')
db.connect()

from back.models.bike import Bike
from back.models.neighbourhood import Location
from back.models.neighbourhood import Neighbourhood, Link
from back.models.postcode import PostCode

db.create_tables([Neighbourhood, Bike, Location, Link, PostCode], safe=True)


class CachingError(ApiError):
    pass


PostCodeLike = Union[PostCode, str]