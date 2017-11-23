from peewee import SqliteDatabase, Model
import glob
import os

from playhouse.shortcuts import model_to_dict


db = SqliteDatabase('data.db')
db.connect()
__all__ = [os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__) + "/*.py")]
