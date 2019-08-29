from flask import Flask

# Enable session.query created with pure sqlalchemy
# from flaskapi.core.database import db_session

from flaskapi.core.redis_config import DecodedRedis
from flaskapi.core.redis_conn import FlaskRedis

# -------------------------------------------
#   APP FACTORY
# -------------------------------------------
"""
RESTPlus is utilized for two purposes only:    
    1. Providing resources class
    2. Swagger documentation
    DO NOT USE MODELS!
    
"""

redis_conn = FlaskRedis.from_custom_provider(
    DecodedRedis, app=None, config_prefix='REDIS')


def create_app(config='Development') -> Flask:
    app = Flask(__name__)
    if config is not None:
        app.config.from_object(f"flaskapi.core.app_config.{config}Config")

    # OPTIONALLY: Use with PostgreSQL integration
    # @app.teardown_appcontext
    # def shutdown_session(exception=None):
    #     db_session.remove()

    init_app(app)
    return app


def init_app(app_obj):
    redis_conn.init_app(app_obj)

    # OPTIONALLY: PostgreSQL
    # Do NOT integrate with docker-compose - use external db instead!
    # from flaskapi.core.database import init_db
    # db.init_app(app)
    # migrate.init_app(app, db)
    # init_db()

    from flaskapi.core.app_setup import route_blueprint
    app_obj.register_blueprint(route_blueprint)

    from flaskapi.apis.resources import api
    api.init_app(app_obj)
