from typing import Union

from peewee import SqliteDatabase

from hyperion.fetch import ApiError

db: SqliteDatabase = SqliteDatabase('data.db')
db.connect()

from hyperion.models.bike import Bike  # noqa: E402
from hyperion.models.neighbourhood import Location  # noqa: E402
from hyperion.models.neighbourhood import Neighbourhood, Link  # noqa: E402
from hyperion.models.postcode import PostCode  # noqa: E402

db.create_tables([Neighbourhood, Bike, Location, Link, PostCode], safe=True)


class CachingError(ApiError):
    pass


PostCodeLike = Union[PostCode, str]
