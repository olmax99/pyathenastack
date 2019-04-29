import pytest
from loansapi import api
from loansapi import database


@pytest.fixture
def client():
    api.app.config['DATABASE'] = 'postgresql://test:test123@testdb/test_api'
    api.app.config['TESTING'] = True
    client = api.app.test_client()

    # TODO: what is an app_context() and from which object is it being created?
    with api.app.app_context():
        database.app_mode = 'TEST'
        database.init_db()

    yield client

    # os.close(db_fd)
    # os.unlink(flaskr.app.config['DATABASE'])
