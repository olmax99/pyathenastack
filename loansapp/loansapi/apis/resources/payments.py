from flask_restplus import Resource
# from loansapi.api import api

from loansapi.database import db_session
from loansapi.models.payments import Payments
# from loansapi.models.payments import AllLoansSchema

"""
A namespace module contains response serializers. CRUD resource declarations should 
be defined using marshmallow and sqlalchemy ORM, which are a more general purpose 
validation/serialization libraries than restplus ( intends to use it in the future
 as well ).

"""

# This is how to access a declarative :
#
# from yourapplication.database import db_session
# >>> from yourapplication.models import User
# >>> u = User('admin', 'admin@localhost')
# >>> db_session.add(u)
# >>> db_session.commit()

# TODO: How to simply read from database?
# This is the pure SQLAlchemy way:
# for item in db_session.query(Users.id, Users.name):
#         print item
#
# ------------------------------------------------------------------------------
# NOTE:
# The Model declarative base class behaves like a regular Python class but has
# a query attribute attached that can be used to query the model.
# (Model and BaseQuery)
# ------------------------------------------------------------------------------
#
# In Flask
# Querying is simple as well:
# >>> User.query.all()
# [<User u'admin'>]
# >>> User.query.filter(User.name == 'admin').first()
# <User u'admin'>

# TODO: How do I write to db?
# You can insert entries into the database like this:
# >>> from yourapplication.database import db_session
# >>> from yourapplication.models import User
# >>> u = User('admin', 'admin@localhost')
# >>> db_session.add(u)
# >>> db_session.commit()

# -----------------------------------------------------
# NOTE:
#   You have to commit the session, but you don’t have
#   to remove it at the end of the request
# -----------------------------------------------------

# from loansapi.database import init_db
# init_db()


# @api.route('/loans')
class AllLoans(Resource):
    def get(self):
        # loans = AllLoans
        # STEP 1: Return query object through sqlalchemy
        loan = Payments.query.filter(Payments.loan_id == 'xqd20166231').first()

        # STEP 2: Apply appropriate schema

        # STEP 3: dump (serialize)
        # return schema.dump(loan)
        return str(loan)


# # @api.route('/loan/<string:loan_id>')
# class DetailLoan(Resource):
#     def get(self, loan_id):
#         # return all loan data
#         # ensure that category mapping is returned as well
#         return {'loan': {'loan_id': loan_id,
#                          'loan_type': 2}}

# What is the difference between flask_restplus models and marshmallow?
# * flask_restplus models are meant to be input validation models and output serializers.
# * create API model from sqlalchemy models using marshmallow. Use the
#   @marshal_list_with(your_model) decorator in order to get the intended output
#
# NOTE: Drop flask-restful marshalling in favor of Marshmallow!!


