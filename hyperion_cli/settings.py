import os

from dotenv import load_dotenv

load_dotenv()

TWITTER_CONSUMER_KEY = os.environ.get("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.environ.get("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

SERVER_HOST = os.getenv("HYPERION_HOST", "0.0.0.0")
SERVER_PORT = os.getenv("HYPERION_PORT", "8080")
