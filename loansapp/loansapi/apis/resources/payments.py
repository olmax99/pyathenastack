from flask_restplus import Resource
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


class AllLoans(Resource):
    def get(self):
        # STEP 1: Return query object through sqlalchemy
        loan = Payments.return_by_id('xqd20166231')

        # STEP 2: Apply appropriate schema
        # STEP 3: dump (serialize)
        return loan.json()


# # @api.route('/loan/<string:loan_id>')
# class DetailLoan(Resource):
#     def get(self, loan_id):
#         # return all loan data
#         # ensure that category mapping is returned as well
#         return {'loan': {'loan_id': loan_id,
#                          'loan_type': 2}}



