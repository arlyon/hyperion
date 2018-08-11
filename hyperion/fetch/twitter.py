import logging
from datetime import timedelta
from typing import List

import aiohttp

import feedparser
from pybreaker import CircuitBreaker

from hyperion import logger
from hyperion.fetch import ApiError


twitrss_breaker = CircuitBreaker(3, timedelta(hours=1))


@twitrss_breaker
async def fetch_twitter(handle: str) -> List:
    """
    Gets the twitter feed for a given handle.
    :param handle: The twitter handle.
    :return: A list of entries in a user's feed.
    :raises ApiError: When the api couldn't connect.
    :raises CircuitBreakerError: When the circuit breaker is open.
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"http://twitrss.me/twitter_user_to_rss/?user={handle}") as request:
                text = await request.text()
        except aiohttp.ClientConnectionError as con_err:
            logger.error(f"Could not connect to {con_err.host}")
            raise ApiError(f"Could not connect to {con_err.host}")
        else:
            feed = feedparser.parse(text)
            for x in feed.entries:
                x["image"] = feed.feed["image"]["href"]
            return feed.entries
