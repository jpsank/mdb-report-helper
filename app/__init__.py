# pylint: disable=wrong-import-position
"""
File for initializing and running flask application.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_session import Session

import config

# Need this for instance
current_dir = os.path.dirname(os.path.realpath(__file__))

# Set up server configuration
app = Flask(__name__, static_folder='static', static_url_path='/static',
            template_folder='templates', instance_relative_config=True)
app.config.from_object(config)
app.config.from_pyfile("config.py")

# Initialize Flask extensions
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

app.config['SESSION_SQLALCHEMY'] = db
sess = Session(app)

with app.app_context():
    from app import util

# Set routes and define models
from app import routes, models
