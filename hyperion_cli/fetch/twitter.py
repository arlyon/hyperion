from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import List, Optional, Dict

from aiobreaker import CircuitBreaker
from dataclasses_json import dataclass_json
from peony import PeonyClient
from peony.exceptions import PeonyException

from . import ApiError
from .. import logger
from ..settings import TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET

twitter_breaker = CircuitBreaker(3, timedelta(hours=1))

client = None


@dataclass_json
@dataclass
class Entities:
    hashtags: List
    symbols: List
    user_mentions: List
    urls: List

    @staticmethod
    def from_api(entities: Dict) -> 'Entities':
        return Entities(
            entities.hashtags,
            entities.symbols,
            entities.user_mentions,
            entities.urls,
        )


@dataclass_json
@dataclass
class Tweet:
    created_at: datetime
    text: str
    entities: Entities
    retweet_count: int
    favorite_count: int

    @staticmethod
    def from_api(tweet: Dict) -> 'Tweet':
        return Tweet(
            datetime.strptime(tweet.created_at, '%a %b %d %H:%M:%S %z %Y'),
            tweet["text"],
            Entities.from_api(tweet.entities),
            retweet_count=tweet.retweet_count,
            favorite_count=tweet.favorite_count,
        )


@dataclass_json
@dataclass
class RecentTweets:
    user: Dict
    tweets: List[Tweet]

    @staticmethod
    def from_api(tweets: List) -> Optional['RecentTweets']:
        if len(tweets) == 0:
            return None

        return RecentTweets(tweets[0].user, [Tweet.from_api(x) for x in tweets])


@twitter_breaker
async def fetch_twitter(handle: str) -> Optional[RecentTweets]:
    """
    Gets the twitter feed for a given handle.
    :param handle: The twitter handle.
    :return: A list of entries in a user's feed.
    :raises ApiError: When the api couldn't connect.
    :raises CircuitBreakerError: When the circuit breaker is open.
    """

    if client is None:
        raise ApiError("Twitter not enabled.")

    try:
        request = await client.api.statuses.user_timeline.get(screen_name=handle)
    except PeonyException as e:
        raise ApiError(e.get_message())

    return RecentTweets.from_api(request.data)


def initialize_twitter():
    global client

    missing = False

    required_keys = [
        ("consumer key", TWITTER_CONSUMER_KEY),
        ("consumer secret", TWITTER_CONSUMER_SECRET),
        ("access token", TWITTER_ACCESS_TOKEN),
        ("access token secret", TWITTER_ACCESS_TOKEN_SECRET),
    ]

    for name in [x for x, y in required_keys if y is None]:
        logger.info(f"Twitter {name} not provided.")
        missing = True

    if missing:
        logger.info("Twitter disabled.")
    else:
        client = PeonyClient(
            consumer_key=TWITTER_CONSUMER_KEY,
            consumer_secret=TWITTER_CONSUMER_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
        )
