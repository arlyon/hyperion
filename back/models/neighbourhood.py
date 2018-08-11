from typing import Iterable, Dict

import peewee as pw
from playhouse.shortcuts import model_to_dict

from .base import BaseModel


class Neighbourhood(BaseModel):
    """
    Contains information about a police neighbourhood.
    """
    name = pw.CharField()
    code = pw.CharField()
    description = pw.CharField(null=True)
    email = pw.CharField(null=True)
    facebook = pw.CharField(null=True)
    telephone = pw.CharField(null=True)
    twitter = pw.CharField(null=True)

    def serialize(self):
        data = model_to_dict(self, backrefs=True)
        data["links"] = data.pop("links")
        data["locations"] = data.pop("locations")
        data.pop("postcodes")
        return data

    @staticmethod
    def from_dict(data):
        neighbourhood = Neighbourhood(
            name=data["name"],
            code=data["id"],
            description=data["description"] if "description" in data else None,
            email=data["contact_details"]["email"] if "email" in data["contact_details"] else None,
            facebook=data["contact_details"]["facebook"] if "facebook" in data["contact_details"] else None,
            telephone=data["contact_details"]["telephone"] if "telephone" in data["contact_details"] else None,
            twitter=data["contact_details"]["twitter"] if "twitter" in data["contact_details"] else None,
        )

        return neighbourhood


class Link(BaseModel):
    """
    Contains a link for a police presence in an area.
    """
    name = pw.CharField()
    url = pw.CharField()
    neighbourhood = pw.ForeignKeyField(Neighbourhood, related_name="links")

    @staticmethod
    def from_dict(neighbourhood, data):
        return [
            Link(
                name=link["title"],
                url=link["url"],
                neighbourhood=neighbourhood,
            )
            for link in data
        ]


class Location(BaseModel):
    """
    Contains data about police stations.
    """
    from . import postcode

    address = pw.CharField()
    description = pw.CharField(null=True)
    latitude = pw.FloatField(null=True)
    longitude = pw.FloatField(null=True)
    name = pw.CharField()
    neighbourhood = pw.ForeignKeyField(Neighbourhood, related_name="locations")
    postcode = pw.ForeignKeyField(postcode.PostCode)
    type = pw.CharField()

    @staticmethod
    def from_dict(neighbourhood, data: Iterable[Dict]):
        return (Location(
            address=location["address"],
            description=location["description"],
            latitude=location["latitude"],
            longitude=location["longitude"],
            name=location["name"],
            neighbourhood=neighbourhood,
            # postcode=postcode,
            # todo sort out postcode saving
            type=location["type"],
        ) for location in data)