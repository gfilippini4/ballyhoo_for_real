from flask import render_template

from app import __init__

app = __init__.create_app()


@app.route('/')
@app.route('/index')
def index():
    return render_template('base_extended.html')
