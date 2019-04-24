from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from loansapi.database import Base

# from loansapi.models.payments import Payments


class Categories(Base):
    __tablename__ = 'categories'
    cat_id = Column("category_id", Integer, primary_key=True)
    loan_type = Column(String)
    loan_max = Column(String)
    term = Column(Integer)
    secured = Column(Boolean)

    # payments = relationship('Payments', lazy='dynamic')

    def __init__(self, loan_type=None, loan_max=None, term=None, secured=None):
        self.loan_type = loan_type
        self.loan_max = loan_max
        self.term = term
        self.secured = secured

    def __repr__(self):
        return f'Loan Category {self.loan_type}'

    def json(self):
        return {
            'id': self.cat_id,
            'type': self.loan_type,
            'max': self.loan_max,
            'term': self.term,
            'secured': self.secured,
            # 'payments': [payment.json() for payment in self.payments.all()]
        }

    @classmethod
    def find_by_type(cls, type_of_loan):
        return cls.query.filter(cls.loan_type == type_of_loan).all()