from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.orm import relationship

from loansapi.database import Base
# from loansapi.api import db


# TODO: How to create Models based on existing database?
# Use declarative_base extension in SQLAlchemy.
# You can either declare the tables in your code, or automatically load them.
# Here, we declare them separately.

# TODO: How to define Schemas?
# Still marshmallow is recommended for serialization

# The Model declarative base class behaves like a regular Python class but has
# a query attribute attached that can be used to query the model.
# (Model and BaseQuery)
class Payments(Base):
    __tablename__ = 'payments'
    loan_id = Column(String(50), primary_key=True)
    status = Column("loan_status", String(50))
    principal = Column(Integer)
    terms = Column(Integer)
    effective_date = Column(Date)
    due_date = Column(Date)
    paid_off_time = Column(DateTime)
    past_due_days = Column(Integer)
    age = Column(Integer)
    education = Column(String)
    gender = Column(String)
    # loan_cat = relationship("Categories", backref="payments", order_by="Categories.cat_id")

    def __init__(self, loan_id=None, status=None, principal=None,
                 terms=None, effective_date=None, due_date=None,
                 paid_off_time=None, past_due_days=None, age=None,
                 education=None, gender=None, loan_cat=None):
        self.loan_id = loan_id
        self.status = status
        self.principal = principal
        self.terms = terms
        self.effective_date = effective_date
        self.due_date = due_date
        self.paid_off_time = paid_off_time
        self.past_due_days = past_due_days
        self.age = age
        self.education = education
        self.gender = gender
        self.loan_cat = loan_cat

    def __repr__(self):
        return f'<Loan Payment with id {self.loan_id}>'


# # create schemas according to request
# class AllLoansSchema(ma.Schema):
#     class Meta:
#         fields = ('loan_id', 'loan_status')
