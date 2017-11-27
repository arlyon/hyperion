from peewee import SqliteDatabase
import glob
import os

db = SqliteDatabase('data.db')
db.connect()

from models.bikes import Bike
from models.location import Location
from models.neighbourhood import Neighbourhood, Link
from models.postcode import PostCodeMapping

db.create_tables([Neighbourhood, Bike, Location, Link, PostCodeMapping], safe=True)
__all__ = [os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__) + "/*.py")]
