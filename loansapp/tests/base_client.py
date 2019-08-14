import pytest

from loansapi import api
from loansapi.core import database
from loansapi.core.redis_config import DecodedRedis
from loansapi.core.redis_conn import FlaskRedis

test_redis = FlaskRedis.from_custom_provider(
    DecodedRedis, app=None, config_prefix='TEST_REDIS')


@pytest.fixture
def client():
    app = api.create_app(config='Testing')
    client = app.test_client()

    with app.app_context():
        database.init_db()
        test_redis.init_app(app)

    yield client


