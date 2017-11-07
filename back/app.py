from datetime import date
from flask import Flask, jsonify, render_template
from peewee import OperationalError

from back.orm import db, Person

app = Flask(__name__)


def connect():
    """
    Connects to the database and sets up some data.
    :return:
    """
    db.connect()

    try:
        db.create_tables([Person])
    except OperationalError:
        print("Tables already exist, no need to create.")

    if Person.select().where(Person.name == 'bob').count() == 0:
        print("No bob, making a new one")
        Person.create(name="bob", birthday=date(1960, 1, 15), is_relative=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/people/<string:name>', methods=['GET'])
@app.route('/api/people/', methods=['GET'])
def person(name=None):
    if name is None:
        return jsonify([p.serialize() for p in Person.select()])
    else:
        try:
            return jsonify(Person.get(Person.name == name).serialize())
        except:
            return jsonify({'error': 'Not Found'}), 404


connect()


if __name__ == '__main__':
    app.run(debug=True)
