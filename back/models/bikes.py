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
    latitude = pw.FloatField(null=True)
    longitude = pw.FloatField(null=True)
    frame_number = pw.TextField(null=True)
    rfid = pw.TextField(null=True)
    description = pw.TextField(null=True)
    reported_at = pw.TextField(null=True)
    cached_date = pw.DateTimeField(default=datetime.datetime.now)

    @staticmethod
    def get_most_recent_bike() -> 'Bike' or None:
        """
        Gets the most recently cached bike from the database.
        :return: The bike that was cached most recently.
        """
        try:
            return Bike.select().order_by(Bike.cached_date.desc()).get()
        except pw.DoesNotExist:
            return None
