from tests.base_client import test_redis
from tests.base_client import client


# General redis read-write
def test_redis_read_write(client):
    test_redis.mset({'uuid': 'lws_dstate_xxx-xxxx-xxxx'})

    assert test_redis.get('uuid') == 'lws_dstate_xxx-xxxx-xxxx'
