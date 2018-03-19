import requests
from flask import jsonify

from back import app
from back.models.util import get_postcode, get_neighbourhood


@app.route('/api/crime/<string:postcode>')
def api_crime(postcode):
    """
    Gets the crime nearby to a given postcode.
    :param postcode: The postcode to lookup.
    :return: A json representation of the crimes near the postcode.
    """
    mapping = get_postcode(postcode)

    crime_lookup = f"https://data.police.uk/api/crimes-street/all-crime?lat={mapping.lat}&lng={mapping.long}"
    crime_request = requests.get(crime_lookup).json()

    return jsonify(crime_request)


@app.route('/api/neighbourhood/<string:postcode>')
def api_neighbourhood(postcode):
    """
    Gets police data about a neighbourhood.
    :param postcode: The postcode to look up.
    :return: The police data for that post code.
    """
    neighbourhood = get_neighbourhood(postcode)
    return jsonify(neighbourhood.serialize()) if neighbourhood is not None else (jsonify(message="No Police Data"), 404)
