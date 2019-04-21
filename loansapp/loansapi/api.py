from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# Create the Connexion application instance
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flask:flasksql@mysql/flask_api'
# makes sure that all changes to the db are committed after each HTTP request
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# imports all pre-defined landing paths
from loansapi.core import app_setup

# imports all api endpoints
from loansapi.apicalls import apicalls





