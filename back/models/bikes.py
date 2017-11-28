import datetime
import peewee as pw

from back.models.base import BaseModel


class Bike(BaseModel):
    """
    The class for the bike model entity.
    """
    make = pw.TextField(null=True)
    model = pw.TextField(null=True)
    colour = pw.TextField(null=True)
    latitude = pw.FloatField()
    longitude = pw.FloatField()
    frame_number = pw.TextField(null=True)
    rfid = pw.TextField(null=True)
    description = pw.TextField(null=True)
    reported_at = pw.TextField(null=True)
    cached_date = pw.DateTimeField(default=datetime.datetime.now)
