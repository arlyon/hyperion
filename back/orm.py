from flask import jsonify
from peewee import *
from playhouse.shortcuts import model_to_dict

db = SqliteDatabase('data.db')


class BaseModel(Model):
    class Meta:
        database = db  # specify the db to use

    def serialize(self):
        return model_to_dict(self)


class Person(BaseModel):
    """
    The person model.
    """
    name = CharField()
    birthday = DateField()
    is_relative = BooleanField()
