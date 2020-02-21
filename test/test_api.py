"""
This module contains integration tests for the http server.

General patterns:

    replace the fetch functions with mocked versions and dummy data
    call the api over http
    assert that the data is as expected
"""
from os import remove

from pytest import mark, fixture

from hyperion_cli.models import initialize_database
from test.util import postcodes_io_ok


@mark.skipif(postcodes_io_ok() is False, reason="Postcodes IO Down!")
@mark.asyncio
class TestApi:

    @fixture(scope="function")
    def db(self):
        path = "test-db.sqlite"

        initialize_database(path)
        yield
        remove(path)

    async def test_postcode(self, db):
        assert False

    async def test_postcode_bikes(self, db):
        assert False

    async def test_postcode_bikes_radius(self, db):
        assert False

    async def test_postcode_crime(self, db):
        assert False

    async def test_postcode_neighbourhood(self, db):
        assert False

    async def test_postcode_nearby(self, db):
        assert False

    async def test_postcode_nearby_radius(self, db):
        assert False
