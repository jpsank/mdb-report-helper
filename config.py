import re
import os
basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

# Flask-SQLAlchemy
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-Session
SESSION_TYPE = 'sqlalchemy'


UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploads')



