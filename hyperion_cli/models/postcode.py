import peewee as pw
from geopy import Point
from geopy.distance import geodesic
from playhouse.shortcuts import model_to_dict

from .base import BaseModel


class Postcode(BaseModel):
    """
    Maps a postcode to a lat and long.
    """
    from .neighbourhood import Neighbourhood

    postcode = pw.CharField()
    lat = pw.FloatField()
    long = pw.FloatField()
    country = pw.CharField()
    district = pw.CharField()
    zone = pw.CharField(null=True)
    neighbourhood = pw.ForeignKeyField(Neighbourhood, null=True, related_name="postcodes")

    def serialize(self):
        return model_to_dict(self, exclude=[Postcode.id])

    def distance_to(self, other: 'Postcode'):
        source = Point(self.lat, self.long)
        destination = Point(other.lat, other.long)
        return geodesic(source, destination).kilometers

    @staticmethod
    def from_dict(data):
        return Postcode(
            postcode=data["postcode"].replace(" ", ""),
            lat=data["latitude"],
            long=data["longitude"],
            country=data["country"],
            district=data["admin_district"],
            zone=data["msoa"]
        )
