
import peewee as pw

from models.base import BaseModel
from models.neighbourhood import Neighbourhood
from models.postcode import PostCodeMapping


class Location(BaseModel):
    """
    Contains data about police stations.
    """
    address = pw.CharField()
    description = pw.CharField(null=True)
    latitude = pw.FloatField(null=True)
    longitude = pw.FloatField(null=True)
    name = pw.CharField()
    neighbourhood = pw.ForeignKeyField(Neighbourhood)
    postcode = pw.ForeignKeyField(PostCodeMapping)
    type = pw.CharField()