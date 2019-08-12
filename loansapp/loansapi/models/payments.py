from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from loansapi.core import database
from loansapi.core.database import Base
# NOTE: This is mistakenly flagged as unreferenced by PyCharm


# The Model declarative base class behaves like a regular Python class but has
# a query attribute attached that can be used to query the model.
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

    loan_cat_id = Column(ForeignKey('categories.category_id'))
    categories = relationship('Categories')
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

    def json(self):
        return {'loan_id': self.loan_id, 'status': self.status, 'loan_cat': self.categories.loan_type}

    @classmethod
    def return_by_id(cls, loan):
        return cls.query.filter(cls.loan_id == loan).first()

    @classmethod
    def save_to_db(cls, pay_object):
        database.db_session.add(pay_object)
        database.db_session.commit()

    @classmethod
    def delete_from_db(cls, pay_object):
        database.db_session.delete(pay_object)
        database.db_session.commit()

# # create schemas according to request
# class AllLoansSchema(ma.Schema):
#     class Meta:
#         fields = ('loan_id', 'loan_status')
