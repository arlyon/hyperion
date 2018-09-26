from urllib.error import URLError
from urllib.request import urlopen


def postcodes_io_ok() -> bool:
    try:
        return urlopen("https://postcodes.io/ping").getcode() == 200
    except URLError:
        return False
