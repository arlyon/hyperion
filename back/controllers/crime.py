import requests
from flask import jsonify

from back import app
from back.models.tools import get_postcode_mapping


@app.route('/api/crime/<string:postcode>')  # assign function to specified route
def get_crime(postcode):
    """
    Gets the crime nearby to a given postcode.
    :param postcode: The postcode to lookup.
    :return: A json representation of the crimes near the postcode.
    """
    mapping = get_postcode_mapping(postcode)

    crime_lookup = f"https://data.police.uk/api/crimes-street/all-crime?lat={mapping.lat}&lng={mapping.long}"
    crime_request = requests.get(crime_lookup).json()

    return jsonify(crime_request)

