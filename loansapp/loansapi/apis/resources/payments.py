from flask_restplus import Resource
from loansapi.models.payments import Payments

"""
A namespace module contains response serializers. CRUD resource declarations should 
be defined using marshmallow and sqlalchemy ORM, which are a more general purpose 
validation/serialization libraries than restplus ( intends to use it in the future
as well ).

"""


class AllLoans(Resource):
    def get(self):
        # STEP 1: Return query object through sqlalchemy
        loan = Payments.return_by_id('xqd20166231')

        # STEP 2: Apply appropriate schema
        # STEP 3: dump (serialize)
        return loan.json()
