import os
from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_marshmallow import Marshmallow
from flask_restplus import Api
# Enable session.query created with pure sqlalchemy
from loansapi.database import db_session
from loansapi.database import init_db
from loansapi.core.config_parser import read_config

from loansapi.apis.resources.payments import AllLoans

"""
RESTPlus is utilized for two purposes only:    
    1. Providing resources
    2. Swagger documentation
    DO NOT USE MODELS 
"""
# -------------------------------------------
#   INITIALIZE FLASK
# -------------------------------------------
app = Flask(__name__)

# TODO: print to log debug in case it cannot be found
app_mode = os.environ['RUN_MODE']
if app_mode != 'TEST':
    db_uri = ''.join(
        ('postgresql+psycopg2://',
         read_config(app_mode)['db_user'], ':',
         read_config(app_mode)['db_passwd'], '@',
         read_config(app_mode)['db_host'], '/',
         read_config(app_mode)['db_name']))
else:
    db_uri = 'postgresql://test:test123@testdb/test_api'

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
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
# The database is initialized depending on RUN_MODE
init_db()


# To use SQLAlchemy in a declarative way with your application,
# Flask will automatically remove database sessions at the end of the request or
# when the application shuts down.
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()










