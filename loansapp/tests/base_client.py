import pytest
from loansapi import api
from loansapi.core import database


@pytest.fixture
def client():
    app = api.create_app()
    client = app.test_client()

    with app.app_context():
        database.init_db()

    yield client


