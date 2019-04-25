from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from loansapi.core.config_parser import read_config

# Create the Connexion application instance
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = ''.join(
    ('postgresql+psycopg2://',
     read_config()['db_user'], ':', 
     read_config()['db_passwd'], '@postgres/',
     read_config()['db_name']))
# makes sure that all changes to the db are committed after each HTTP request
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# imports all pre-defined landing paths
from loansapi.core import app_setup

# imports all api endpoints
from loansapi.apicalls import apicalls





