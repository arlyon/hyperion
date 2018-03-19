import unittest

from api.bikeregister import get_new_bikes_from_api
from api.police import get_neighbourhood_from_api
from api.postcodes import get_postcode_from_api
from models.util import get_postcode


class TestPostcodeApi(unittest.TestCase):
    """
    Test cases for the post code api.
    """

    def test_api(self):
        """
        Makes sure the function returns the expected result.
        :return:
        """
        postcode = get_postcode_from_api("EH47BL")
        self.assertEqual(postcode.postcode, "EH47BL")


class TestPoliceApi(unittest.TestCase):
    """
    Test cases for the police data api.
    """

    def test_api(self):
        """
        Makes sure the function runs without errors.
        :return:
        """
        postcode = get_postcode("EH47BL")
        neighbourhood = get_neighbourhood_from_api(postcode)


class TestBikeRegisterApi(unittest.TestCase):
    """
    Test cases for the bike register api.
    """

    def test_api(self):
        """
        Makes sure the function runs without errors.
        :return:
        """
        bikes = get_new_bikes_from_api()
        self.assertIsInstance(bikes, list)
