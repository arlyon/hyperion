from flask import Flask, jsonify, render_template, Response
from peewee import OperationalError
import requests

from back.orm import db, Person, PostCodeMapping, DoesNotExist

# create a new instance of the flask class
app = Flask(__name__)


@app.route('/')
def index():
    """
    Returns the index.html template using Jinja.
    :return: The html we want to render.
    """
    return render_template('index.html')


@app.route('/api/people/<string:name>', methods=['GET'])
@app.route('/api/people/', methods=['GET'])
def person(name=None):
    """
    Handles api requests at the /api/people/ endpoint.
    :param name: The name to search. Defaults to none.
    :return: The json for the people that match the query.
    """
    if name is None:
        return jsonify([p.serialize() for p in Person.select()])  # Person.select selects all people (with peewee)
    else:
        try:
            return jsonify(Person.get(Person.name == name).serialize())  # Person.get gets one person (or throws error)
        except DoesNotExist:
            return jsonify({'error': 'Not Found'}), 404


@app.route('/api/crime/<string:postcode>')
def get_crime(postcode):
    """
    Gets the crime nearby to a given postcode.
    :param postcode: The postcode to lookup.
    :return: A json representation of the crimes near the postcode.
    """
    try:
        mapping = PostCodeMapping.get(PostCodeMapping.postcode == postcode)
    except DoesNotExist:
        postcode_lookup = f"http://api.postcodes.io/postcodes/{postcode}"
        postcode_request = requests.get(postcode_lookup).json()

        if postcode_request["status"] == 404:
            return jsonify({'error': postcode_request["error"]}), 404

        lat = round(postcode_request["result"]["latitude"], 6)
        long = round(postcode_request["result"]["longitude"], 6)

        PostCodeMapping.create(postcode=postcode, lat=lat, long=long)  # the peewee function for creating new entities
    else:
        lat = mapping.lat
        long = mapping.long

    # todo: devise way to cache police api (although they are generous)

    crime_lookup = f"https://data.police.uk/api/stops-street?lat={lat}&lng={long}"  # the street stops at a lat/lng
    crime_request = requests.get(crime_lookup).json()  # get the json and parse it immediately

    return jsonify(crime_request)  # jsonify is a flask function that tells flask to make the response json (not html)


if __name__ == '__main__':
    db.connect()
    app.run(debug=True, port=2020)