from flask import render_template
from back import app


@app.route('/')
def index():
    """
    Returns the index.html template using Jinja.
    :return: The html we want to render.
    """
    return render_template('index.html')


@app.route('/service-worker.js')
def service_worker():
    """
    Serves the service worker from the root.
    :return: The service worker.
    """
    return app.send_static_file('service-worker.js')
