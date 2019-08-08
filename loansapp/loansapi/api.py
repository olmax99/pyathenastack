import os
from flask import Flask

# Enable session.query created with pure sqlalchemy
from loansapi.database import db_session


# -------------------------------------------
#   APP FACTORY
# -------------------------------------------
"""
RESTPlus is utilized for two purposes only:    
    1. Providing resources
    2. Swagger documentation
    DO NOT USE MODELS 
"""


def create_app(config='Development'):
    app = Flask(__name__)
    app.config.from_object(f"loansapi.core.app_config.{config}Config")

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    init_app(app)
    return app


def init_app(app_obj):
    # db.init_app(app)
    # migrate.init_app(app, db)
    from loansapi.database import init_db
    init_db()

    from loansapi.core.app_setup import route_blueprint
    app_obj.register_blueprint(route_blueprint)

    from loansapi.apis.resources import api
    api.init_app(app_obj)


# NEEDED by client in tests/base_client.py
RUN_MODE = os.environ['RUN_MODE'].title()
app = create_app(config=RUN_MODE)
