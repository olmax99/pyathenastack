import pytest
from loansapi import api
from loansapi import database
from loansapi.core.config_parser import read_config


@pytest.fixture
def client():
    database_uri = ''.join(
        ('postgresql+psycopg2://',
         read_config('TEST')['db_user'], ':',
         read_config('TEST')['db_passwd'], '@',
         read_config('TEST')['db_host'], '/',
         read_config('TEST')['db_name']))
    api.app.config['DATABASE'] = database_uri
    api.app.config['TESTING'] = True
    client = api.app.test_client()

    # TODO: what is an app_context() and from which object is it being created?
    with api.app.app_context():
        database.app_mode = 'TEST'
        database.init_db()

    yield client

    # os.close(db_fd)
    # os.unlink(flaskr.app.config['DATABASE'])