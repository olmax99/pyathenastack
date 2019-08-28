import pytest


@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'redis://:test456@redis.testing:6379/0',
        'result_backend': 'redis://:test456@redis.testing:6379/0'
    }
