from peewee import Model
from playhouse.shortcuts import model_to_dict

from back.models import db


class BaseModel(Model):
    """
    Defines some base properties for a model.
    """

    def serialize(self):
        return model_to_dict(self)

    class Meta:
        database = db  # specify the db to use
