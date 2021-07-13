import os

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from flask_login import LoginManager
from flask_bootstrap import Bootstrap


app_dir = os.path.abspath(os.path.dirname(__file__))


# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
# Flask-Login
login = LoginManager()
login.login_view = 'auth.login'
# Flask-Session
sess = Session()


def create_app():
    # Create application
    app = Flask(__name__, static_folder='static', static_url_path='/static',
                template_folder='templates', instance_relative_config=True)
    app.config.from_mapping(
        DEBUG=False,
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'data.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_TYPE='sqlalchemy',
        UPLOAD_FOLDER=os.path.join(app_dir, 'static/uploads'),
    )
    app.config.from_pyfile('config.py', silent=True)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize Sentry if possible
    if app.config['SENTRY_DSN']:
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[FlaskIntegration(), SqlalchemyIntegration()]
        )

    # Bind Flask extensions to application object
    db.init_app(app)
    migrate.init_app(app, db)

    bootstrap.init_app(app)
    login.init_app(app)

    app.config['SESSION_SQLALCHEMY'] = db
    sess.init_app(app)

    # Blueprints
    from app.blueprints.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.blueprints.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        from app.util import filters

    return app


from app import models
