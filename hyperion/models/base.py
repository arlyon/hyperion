from peewee import Model, SqliteDatabase
from playhouse.shortcuts import model_to_dict

from . import db


class BaseModel(Model):
    """
    Defines some base properties for a model.
    """

    def serialize(self):
        return model_to_dict(self)

    class Meta:
        database: SqliteDatabase = db
