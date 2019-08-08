from flask_restplus import Api
from loansapi.apis.resources.payments import AllLoans

api = Api(prefix='/api/v0.0')
api.add_resource(AllLoans, '/loans')
