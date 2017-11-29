from flask import jsonify

from back import app
from back.models.tools import get_bikes_from_db


@app.route('/api/bikes/<string:postcode>')
@app.route('/api/bikes/<string:postcode>/<int:radius>')
def get_bikes(postcode, radius=10):
    """
    Gets stolen bikes within a radius of a given postcode.
    :param postcode: The postcode to look up.
    :param radius: The radius to get bikes inside.
    :return: The bikes stolen with the given range from a postcode.
    """
    return jsonify([bike.serialize() for bike in get_bikes_from_db(postcode, radius)])
