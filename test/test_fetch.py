from pytest import mark

from test.util import postcodes_io_ok


@mark.skipif(postcodes_io_ok() is False, reason="Postcodes IO Down!")
@mark.asyncio
class TestApi:

    async def test_true(self):
        assert False
