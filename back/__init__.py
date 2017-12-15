from flask import Flask
from flask_sslify import SSLify
import os
import sys

app = Flask('project', template_folder='back/templates', static_folder='back/static')

# if running on heroku
if 'DYNO' in os.environ:
    print("Running App in Production Mode")
    sys.stdout.flush()
    SSLify(app)
    app.debug = False
    app.config = os.environ.get('FLASK_KEY')
else:
    print("Running App in Debug Mode")
    sys.stdout.flush()
    app.debug = True
    app.config['SECRET_KEY'] = 'dev'

from back.controllers import *