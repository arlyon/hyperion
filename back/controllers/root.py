from flask import render_template
from back import app


@app.route('/')
def index():
    """
    Returns the index.html template using Jinja.
    :return: The html we want to render.
    """
    return render_template('index.html')
