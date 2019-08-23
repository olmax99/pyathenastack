import os
import time
import logging

# from redis import RedisError
from celery import Celery

import utilities
from sbapi_permits.permits_object import PermitsAthena

# NOTE: Redis can only be reached via Celery.Backend, because task is in different container
# from ..loansapp.loansapi.core import redis_conn

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379'),
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')

celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

logger = logging.getLogger(__name__)


@celery.task(name='tasks.add')
def add(x: int, y: int) -> int:
    time.sleep(5)
    return x + y


@celery.task(name='tasks.getsbapermits')
def get_sba_permits(job_id: str, long_job_id: str):
    sync_athena = PermitsAthena(current_uuid=job_id)

    fac = utilities.HookFactory()
    reader = fac.create(type_hook='http', chunk_size=200)

    # try:
    #     redis_conn.set(long_job_id, 'active')
    # except RedisError as e:
    #     print(f"Redis{e.__class__.__name__}: could not write job status '{{{job_id}: 'active'}}'.")

    logger.info('WebApi: job started "get sba-permits"')

    target_url = os.getenv('PERMITS_URL', None)
    headers = {"x-api-key": f"{os.getenv('PERMITS_KEY', None)}"}

    with reader.loading_from(target_url=target_url,
                             hearders=headers,
                             chunks=False) as http_data:
        sync_athena.permits_to_parquet(source_iterable=http_data,
                                       parquet_file=f"{job_id}",
                                       chunks=False)
    
    # try:
    #     redis_conn.set(long_job_id, 'finished')
    # except RedisError as e:
    #     print(f"Redis{e.__class__.__name__}: could not write job status '{{{job_id}: 'finished'}}'.")

    logger.info(f"WebApi: get sba-permits finished - '{job_id}'")

