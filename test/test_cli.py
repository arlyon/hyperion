"""
This module contains integration tests for the command line interface.
"""

from os import remove

from pytest import mark, fixture

from hyperion.cli import cli
from hyperion.models import initialize_database
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

    async def test_postcodes(self, db):
        await cli(("eh47bl",), 0)
