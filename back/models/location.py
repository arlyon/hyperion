
import peewee as pw

from back.models.base import BaseModel
from back.models.neighbourhood import Neighbourhood
from back.models.postcode import PostCodeMapping


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
