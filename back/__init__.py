from flask import Flask
from flask_cors import CORS

app = Flask('project', template_folder='back/templates', static_folder='back/static')
CORS(app)
app.config['SECRET_KEY'] = 'secret'
app.debug = True

from back.controllers import *