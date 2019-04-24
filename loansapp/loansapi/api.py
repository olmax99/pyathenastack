from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restplus import Api

# Load the resources
# from loansapi.apis.ns_loans import api
# Enable session.query created with pure sqlalchemy
from loansapi.database import db_session

"""
RESTPlus is utilized for two purposes only:    
    1. Providing resources, DO NOT USE MODELS  
    2. Swagger documentation

"""

api = Api()

app = Flask(__name__)

# TODO: Replace password in docker and here with secret.ini file logic
# TODO: Also provide env context: development and testing db
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://flask:flaskdb@postgres/flask_api'
# makes sure that all changes to the db are committed after each HTTP request
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# flask_sqlalchemy can be used optionally to pure sqlalchemy
# It offers Flask optimization (vaguely described) and convenience classes,
# e.g. query paginator,
db = SQLAlchemy(app)
ma = Marshmallow(app)

# imports all pre-defined landing paths
from loansapi.core import app_setup


api.init_app(app)

# TODO: Teardown is triggering crash
# # To use SQLAlchemy in a declarative way with your application,
# # Flask will automatically remove database sessions at the end of the request or
# # when the application shuts down.
# @app.teardown_appcontext
# def shutdown_session():
#     db_session.remove()





