import os

from flask import Flask
from flask_sslify import SSLify

app = Flask('project', template_folder='back/templates', static_folder='back/static')

# if running on heroku
if 'DYNO' in os.environ:
    SSLify(app)
    app.debug = False
    app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
else:
    app.debug = True
    app.config['SECRET_KEY'] = 'dev'

from back.controllers import *