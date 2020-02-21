from abc import ABC, abstractmethod

from ..models.util import get_postcode, get_postcodes_from_coordinates, get_postcode_random
from ..util import is_uk_postcode


class PostcodeGetter(ABC):
    """
    Provides postcodes.
    """

    @abstractmethod
    async def get_postcodes(self):
        pass

    @staticmethod
    @abstractmethod
    def can_provide(to_test):
        """
        Checks if the input string is an instance.
        :param to_test:
        :return:
        """
        pass


class PostcodeFromString(PostcodeGetter):

    def __init__(self, postcode):
        self.postcode = postcode

    @staticmethod
    def can_provide(to_test):
        return is_uk_postcode(to_test) if isinstance(to_test, str) else False

    async def get_postcodes(self):
        return [await get_postcode(self.postcode)]

    def __repr__(self):
        return "fuck"


class PostcodeFromCoordinates(PostcodeGetter):

    def __init__(self, coordinates):
        self.lat, self.long = map(float, coordinates.split(","))

    @staticmethod
    def can_provide(to_test):
        if not isinstance(to_test, str):
            return False

        if "," in to_test:
            try:
                items = to_test.split(",")
                assert len(items) == 2
                lat, long = map(float, items)
                assert -90 < lat < 90
                assert -180 < long < 180
            except (ValueError, AssertionError):
                pass
            else:
                return True
        return False

    async def get_postcodes(self):
        return await get_postcodes_from_coordinates(self.lat, self.long)

    def __repr__(self):
        return f'"{self.lat}, {self.long}"'


class PostcodeFromRandom(PostcodeGetter):

    async def get_postcodes(self):
        return [await get_postcode_random() for _ in range(self.count)]

    @staticmethod
    def can_provide(to_test):
        try:
            return int(to_test) > 0
        except ValueError:
            return False

    def __init__(self, count):
        self.count = int(count)

    def __repr__(self):
        return f"{self.count} random postcode{'s' if self.count > 0 else ''}"


getters = [PostcodeFromCoordinates, PostcodeFromString, PostcodeFromRandom]
