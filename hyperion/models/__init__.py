"""
The models package hosts the io for the database, currently through peewee.
"""

from os.path import expanduser, join
from typing import Union, Optional

from peewee import SqliteDatabase

from hyperion.fetch import ApiError
from .base import database_proxy
from .bike import Bike
from .neighbourhood import Location, Neighbourhood, Link
from .postcode import Postcode

PostCodeLike = Union[Postcode, str]


class CachingError(ApiError):
    pass


def initialize_database(path: Optional[str] = None):
    path = path if path is not None else join(expanduser("~"), '.hyperion.db')
    database = SqliteDatabase(path)
    database_proxy.initialize(database)
    database.connect()
    database.create_tables([Neighbourhood, Bike, Location, Link, Postcode], safe=True)
