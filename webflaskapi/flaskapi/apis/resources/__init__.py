from flask_restplus import Api
from flaskapi.apis.resources.sbapipermits import ns as ns1

api = Api()

api.add_namespace(ns1, path='/api/v0.0/permits')
# api.add_resource(PermitsReport, '/permits')
