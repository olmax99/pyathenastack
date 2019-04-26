from loansapi.models.payments import Payments
from datetime import date, datetime

'''
NOTE:   There is no app.test_client() needed, since the tests run inside docker
        in RUN_MODE "TEST" against the test database attached to the Flask Api.

'''


def test_create_payment():
    pay = Payments(loan_id='xqd20166231',
                   status='PAIDOFF',
                   principal=1000,
                   terms=15,
                   effective_date=date(2016, 12, 1),
                   due_date=date(2017, 1, 1),
                   paid_off_time=datetime(2016, 12, 1, 19, 31, 44, 31),
                   past_due_days=None,
                   age=45,
                   education='college',
                   gender='female',
                   loan_cat=1)

    assert pay.loan_id == 'xqd20166231'
    assert pay.status == 'PAIDOFF'
    assert pay.principal == 1000
    assert pay.terms == 15
    assert pay.effective_date == date(2016, 12, 1)
    assert pay.due_date == date(2017, 1, 1)
    assert pay.paid_off_time == datetime(2016, 12, 1, 19, 31, 44, 31)
    assert pay.past_due_days is None
    assert pay.age == 45
    assert pay.education == 'college'
    assert pay.gender == 'female'
    assert pay.loan_cat == 1
