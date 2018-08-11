import datetime
from typing import Optional

import peewee as pw
from playhouse.shortcuts import model_to_dict

from .base import BaseModel


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

    def serialize(self):
        return model_to_dict(self, exclude=[Bike.cached_date, Bike.id])

    @staticmethod
    def get_most_recent_bike() -> Optional['Bike']:
        """
        Gets the most recently cached bike from the database.
        :return: The bike that was cached most recently.
        """
        try:
            return Bike.select().order_by(Bike.cached_date.desc()).get()
        except pw.DoesNotExist:
            return None

    @staticmethod
    def from_dict(data: dict) -> 'Bike':
        return Bike(
            make=data["make"],
            model=data["model"],
            colour=data["colour"],
            latitude=data["latitude"] if not data["latitude"] == "" else None,
            longitude=data["longitude"] if not data["longitude"] == "" else None,
            frame_number=data["frame_number"],
            rfid=data["rfid"],
            description=data["description"],
            reported_at=data["reported_at"]
        )