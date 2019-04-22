from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from loansapi.apis import api

"""
RESTPlus is utilized for two purposes only:    
    1. Providing resources, DO NOT USE MODELS ( Marshmallow does provide that ) 
    2. Swagger documentation

"""
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flask:flasksql@mysql/flask_api'
# makes sure that all changes to the db are committed after each HTTP request
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
ma = Marshmallow(app)

# imports all pre-defined landing paths
from loansapi.core import app_setup

api.init_app(app)





