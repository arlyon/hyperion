import re
from asyncio.locks import Event
from typing import Dict, Tuple, Generic, TypeVar

from hyperion_cli import logger

T = TypeVar('T')

postcode_regex = re.compile("^([Gg][Ii][Rr] 0[Aa]{2})|"
                            "((([A-Za-z][0-9]{1,2})|"
                            "(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|"
                            "(([A-Za-z][0-9][A-Za-z])|"
                            "([A-Za-z][A-Ha-hJ-Yj-y][0-9]?[A-Za-z])))) ?"
                            "[0-9][A-Za-z]{2})$")


def is_uk_postcode(postcode: str) -> bool:
    return re.match(postcode_regex, postcode) is not None


def dataloader(func):
    """
    Allows multiple parallel calls of the same
    async function 'memoize. Handy if a server
    is making multiple of the same request.
    """

    requests: Dict[Tuple, DataEvent] = {}

    async def inner_func(*args):
        key = tuple(args)

        if key in requests:
            logger.debug(f"Call to {func.__name__} waiting for loader")
            response = await requests[key].wait()
        else:
            logger.debug(f"Protecting {func.__name__} with data loader")
            requests[key] = DataEvent()
            response = await func(*args)
            requests[key].send(response)
            del requests[key]
        return response

    return inner_func


class DataEvent(Generic[T]):

    def __init__(self):
        self._event = Event()
        self._data = None

    async def wait(self) -> T:
        if self._sent:
            raise Exception("Data Event Has Happened")

        await self._event.wait()
        return self._data

    def reset(self):
        self._data = None
        self._event.clear()

    def send(self, data: T):
        self._data = data
        self._event.set()

    @property
    def _sent(self):
        return self._event.is_set()
