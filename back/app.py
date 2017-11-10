from flask import Flask, jsonify, render_template
from peewee import OperationalError

from back.orm import db, Person


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
        # if no name is set, return all by selecting and serializing all people
        return jsonify([p.serialize() for p in Person.select()])
    else:
        try:
            # try and get the person whos name matches the input
            return jsonify(Person.get(Person.name == name).serialize())
        except:
            # return a 404 error
            return jsonify({'error': 'Not Found'}), 404


def connect_to_db():
    """
    Connects to the database and creates the schema.
    :return:
    """
    db.connect()

    try:
        db.create_tables([Person])
    except OperationalError:
        print("Tables already exist, no need to create.")


if __name__ == '__main__':
    connect_to_db()
    app.run(debug=True, port=2020)
