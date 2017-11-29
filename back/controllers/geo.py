import requests
from flask import jsonify
from back import app
from back.models.tools import get_postcode_mapping


@app.route('/api/postcode/<string:postcode>')
def get_postcode(postcode):
    """
    Gets data from a postcode.
    :param postcode: The postcode to look up.
    :return: The mapping for the postcode.
    """
    mapping = get_postcode_mapping(postcode)
    return jsonify(mapping.serialize()) if mapping is not None else (jsonify(message="Invalid Postcode"), 404)


@app.route('/api/nearby/<string:postcode>')
@app.route('/api/nearby/<string:postcode>/<int:limit>')
def get_nearby(postcode: str, limit=10):
    """
    Gets wikipedia articles near a given postcode.
    :param postcode: The UK postcode to look up.
    :param limit: The number of results to return.
    :return: The data or an error.
    """
    mapping = get_postcode_mapping(postcode)
    if mapping is None:
        return jsonify(error=404, message="Invalid Postcode"), 404
    request_url = f"https://en.wikipedia.org/w/api.php?action=query&list=geosearch&gscoord={mapping.lat}%7C{mapping.long}&gsradius=10000&gslimit={limit}&format=json"
    request = requests.get(request_url)
    try:
        return jsonify(request.json()["query"]["geosearch"])
    except KeyError:
        return jsonify(message="No Results"), 404
