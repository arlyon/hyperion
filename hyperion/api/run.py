from hyperion.models import initialize_database
from . import app
from .util import enable_cross_origin

initialize_database()
enable_cross_origin(app)
