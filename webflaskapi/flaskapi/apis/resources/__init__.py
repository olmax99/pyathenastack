from flask_restplus import Api
from flaskapi.apis.resources.sbapipermits import PermitsReport

api = Api(prefix='/api/v0.0')
api.add_resource(PermitsReport, '/permits')
