import peewee as pw
from playhouse.shortcuts import model_to_dict

from back.models.base import BaseModel
from back.models.neighbourhood import Neighbourhood


class PostCodeMapping(BaseModel):
    """
    Maps a postcode to a lat and long.
    """
    postcode = pw.CharField()
    lat = pw.FloatField()
    long = pw.FloatField()
    country = pw.CharField()
    district = pw.CharField()
    zone = pw.CharField()
    neighbourhood = pw.ForeignKeyField(Neighbourhood, null=True, related_name="postcodes")

    def serialize(self):
        return model_to_dict(self, exclude=[PostCodeMapping.id])
