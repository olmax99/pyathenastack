from loansapi.models.payments import Payments
from datetime import date, datetime
from tests.base_client import client

'''
NOTE:   app.test_client() is needed, since the tests run inside docker
        in RUN_MODE "TEST" against the test database attached to the Flask Api.

'''


def test_payment_crud(client):
    new_entry = Payments(loan_id='xqd20166231',
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

    assert Payments.return_by_id('xqd20166231') is None
    Payments.save_to_db(new_entry)
    assert Payments.return_by_id('xqd20166231') is not None
    Payments.delete_from_db(new_entry)
    assert Payments.return_by_id('xqd20166231') is None
