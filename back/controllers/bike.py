from flask import jsonify

from back import app
from back.models.tools import get_bikes_from_db


@app.route('/api/bikes/<string:postcode>')
def get_bikes(postcode):
    return jsonify([bike.serialize() for bike in get_bikes_from_db(postcode)])
