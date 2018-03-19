from flask import jsonify

from back import app
from back.models.util import get_stolen_bikes


@app.route('/api/bikes/<string:postcode>')
@app.route('/api/bikes/<string:postcode>/<int:radius>')
def api_bikes(postcode, radius=10):
    """
    Gets stolen bikes within a radius of a given postcode.
    :param postcode: The postcode to look up.
    :param radius: The radius to get bikes inside.
    :return: The bikes stolen with the given range from a postcode.
    """
    return jsonify([bike.serialize() for bike in get_stolen_bikes(postcode, radius)])
