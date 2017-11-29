import feedparser
from flask import jsonify

from back import app


@app.route('/api/rss/<handle>')
def twitter_feed(handle):
    """
    Gets the twitter feed from a given handle.
    :param handle: The twitter handle to find.
    :return: The feed in json format.
    """
    feed = feedparser.parse(f"http://twitrss.me/twitter_user_to_rss/?user={handle}")
    for x in feed.entries:
        x["image"] = feed.feed["image"]["href"]
    return jsonify(feed.entries)