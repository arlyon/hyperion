from os.path import expanduser, join
from typing import Union, Optional

from peewee import SqliteDatabase

from hyperion.fetch import ApiError
from .base import database_proxy
from .bike import Bike
from .neighbourhood import Location, Neighbourhood, Link
from .postcode import PostCode

PostCodeLike = Union[PostCode, str]


class CachingError(ApiError):
    pass


def initialize_database(path: Optional[str]):
    path = path if path is not None else join(expanduser("~"), '.hyperion.db')
    database = SqliteDatabase(path)
    database_proxy.initialize(database)
    database.connect()
    database.create_tables([Neighbourhood, Bike, Location, Link, PostCode], safe=True)
