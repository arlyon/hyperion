from flask import Flask

app = Flask('project', template_folder='back/templates', static_folder='back/static')
app.config['SECRET_KEY'] = 'secret'
app.debug = True

from back.controllers import *