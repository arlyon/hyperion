from peewee import *
from playhouse.shortcuts import model_to_dict

db = SqliteDatabase('data.db')


class BaseModel(Model):
    """
    Defines some base properties for a model.
    """

    class Meta:
        database = db  # specify the db to use

    def serialize(self):
        return model_to_dict(self)


class Neighbourhood(BaseModel):
    """
    Contains information about a police neighbourhood.
    """
    name = CharField()
    code = CharField()
    description = CharField(null=True)
    email = CharField(null=True)
    facebook = CharField(null=True)
    telephone = CharField(null=True)
    twitter = CharField(null=True)

    def serialize(self):
        data = model_to_dict(self, backrefs=True)
        data["links"] = data.pop("link_set")
        data["locations"] = data.pop("location_set")
        data.pop("postcodemapping_set")
        return data


class Link(BaseModel):
    name = CharField()
    url = CharField()
    neighbourhood = ForeignKeyField(Neighbourhood)


class PostCodeMapping(BaseModel):
    """
    Maps a postcode to a lat and long.
    """
    postcode = CharField()
    lat = FloatField()
    long = FloatField()
    country = CharField()
    district = CharField()
    zone = CharField()
    neighbourhood = ForeignKeyField(Neighbourhood, null=True)

    def serialize(self):
        return model_to_dict(self, exclude=[PostCodeMapping.id])


class Location(BaseModel):
    """
    Contains data about police stations.
    """
    address = CharField()
    description = CharField(null=True)
    latitude = FloatField(null=True)
    longitude = FloatField(null=True)
    name = CharField()
    neighbourhood = ForeignKeyField(Neighbourhood)
    postcode = ForeignKeyField(PostCodeMapping)
    type = CharField()
