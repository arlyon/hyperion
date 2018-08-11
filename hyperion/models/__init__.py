from typing import Union

from peewee import SqliteDatabase

from hyperion.fetch import ApiError

db = SqliteDatabase('data.db')
db.connect()

from hyperion.models.bike import Bike
from hyperion.models.neighbourhood import Location
from hyperion.models.neighbourhood import Neighbourhood, Link
from hyperion.models.postcode import PostCode

db.create_tables([Neighbourhood, Bike, Location, Link, PostCode], safe=True)


class CachingError(ApiError):
    pass


PostCodeLike = Union[PostCode, str]
