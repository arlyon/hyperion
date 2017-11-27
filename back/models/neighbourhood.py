import peewee as pw
from playhouse.shortcuts import model_to_dict
from back.models.base import BaseModel


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
        data["links"] = data.pop("link_set")
        data["locations"] = data.pop("location_set")
        data.pop("postcodemapping_set")
        return data


class Link(BaseModel):
    name = pw.CharField()
    url = pw.CharField()
    neighbourhood = pw.ForeignKeyField(Neighbourhood)

