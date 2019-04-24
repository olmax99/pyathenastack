from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restplus import Api

from loansapi.database import db_session
from loansapi.database import init_db

from loansapi.apis.resources.payments import AllLoans

# Enable session.query created with pure sqlalchemy




"""
RESTPlus is utilized for two purposes only:    
    1. Providing resources, DO NOT USE MODELS  
    2. Swagger documentation

"""
# -------------------------------------------
#   INITIALIZE FLASK
# -------------------------------------------
app = Flask(__name__)

# TODO: Replace password in docker and here with secret.ini file logic
# TODO: Also provide env context: development and testing db
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://flask:flaskdb@postgres/flask_api'
# makes sure that all changes to the db are committed after each HTTP request
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

api = Api(app)

# -------------------------------------------
#   LOAD STATICS AND RESOURCES
# -------------------------------------------

# imports all pre-defined landing paths
from loansapi.core import app_setup

api.add_resource(AllLoans, '/api/loans')

# -------------------------------------------
#   CREATE DB
# -------------------------------------------
# TODO: Initialize db depending on testing mode or development
init_db()

# # flask_sqlalchemy can be used optionally to pure sqlalchemy
# # It offers Flask optimization (vaguely described) and convenience classes,
# # e.g. query paginator,
# db = SQLAlchemy(app)
# ma = Marshmallow(app)


# To use SQLAlchemy in a declarative way with your application,
# Flask will automatically remove database sessions at the end of the request or
# when the application shuts down.
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()










