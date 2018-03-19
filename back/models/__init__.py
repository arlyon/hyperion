import glob
import os

from peewee import SqliteDatabase

db = SqliteDatabase('data.db')
db.connect()

from back.models.bikes import Bike
from back.models.location import Location
from back.models.neighbourhood import Neighbourhood, Link
from back.models.postcode import PostCodeMapping

db.create_tables([Neighbourhood, Bike, Location, Link, PostCodeMapping], safe=True)
__all__ = [os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__) + "/*.py")]
