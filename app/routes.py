from flask import render_template
from . import db
from flask import current_app as app

@app.route('/')
def home():
    return render_template('home.html')
