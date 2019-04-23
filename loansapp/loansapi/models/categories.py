from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

from loansapi.database import Base


class Categories(Base):
    __tablename__ = 'categories'
    cat_id = Column("category_id", Integer, primary_key=True)
    loan_id = Column(ForeignKey('payments.id'))
    loan_type = Column(String)
    loan_max = Column(String)
    term = Column(Integer)
    secured = Column(Boolean)

    def __init__(self, loan_type=None, loan_max=None, term=None, secured=None):
        self.loan_type = loan_type
        self.loan_max = loan_max
        self.term = term
        self.secured = secured

    def __repr__(self):
        return f'Loan Category {self.loan_type}'