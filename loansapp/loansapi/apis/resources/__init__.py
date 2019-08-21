from flask_restplus import Api
from loansapi.apis.resources.payments import AllLoans
from loansapi.apis.resources.sbapipermits import PermitsReport

api = Api(prefix='/api/v0.0')
api.add_resource(AllLoans, '/loans')
api.add_resource(PermitsReport, '/permits')
