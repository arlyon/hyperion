from flask import json, jsonify

from back import app


@app.route('/api/bikes/')
def get_bikes():
    with open("../stolenbikes.json", "r") as f:
        bikesdata = json.load(f)
    return jsonify(bikesdata[:100])
