from flask_restplus import Resource
from loansapi.api import api

"""
A namespace module contains response serializers. CRUD resource declarations should 
be defined using marshmallow and sqlalchemy ORM, which are a more general purpose 
validation/serialization libraries than restplus ( intends to use it in the future
 as well ).

"""


@api.route('/loans')
class AllLoans(Resource):
    def get(self):
        # return all loan IDs
        return {'loans': []}


@api.route('/loan/<string:loan_id>')
class DetailLoan(Resource):
    def get(self, loan_id):
        # return all loan data
        # ensure that category mapping is returned as well
        return {'loan': {'loan_id': loan_id,
                         'loan_type': 2}}

# TODO: What is the difference between flask_restplus models and marshmallow ORM?
# * flask_restplus models are meant to be input validation models and output serializers.
# * create API model from sqlalchemy models using marshmallow. Use the
#   @marshal_list_with(your_model) decorator in order to get the intended output
#
# NOTE: Drop flask-restful marshalling in favor of Marshmallow!!

# Serializing Objects:
# --------------------
# Return values will behave normal for std Python data structures,
# but will fail for objects:
# from collections import OrderedDict
# use '@marshal_with' decorator ( able to serialize field objects )
# and in Model e.g. 'uri': fields.Url()


# 'marshal_with' basically returns data as OrderedDict
# @api.marshal_with(loans, envelope='resource')
# def get(self):
#     pass
