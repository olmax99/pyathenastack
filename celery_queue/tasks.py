import os
import time
from datetime import datetime
import logging

# from redis import RedisError
from celery import Celery
from celery.utils.log import get_task_logger

import utilities
from sbapi_permits.permits_object import PermitsAthena

# NOTE: Redis can only be reached via Celery.Backend, because task is in different container
# from ..loansapp.loansapi.core import redis_conn

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://:test456@redis.testing:6379/0'),
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://:test456@redis.testing:6379/0')

celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

logger = get_task_logger(__name__)


class TaskFailure(Exception):
    pass


# TODO: Add schema verfification for input variables
@celery.task(name='tasks.getsbapermits')
def get_sba_permits(job_id: str, long_job_id: str, dt_called):
    sync_athena = PermitsAthena(current_uuid=job_id, partitiontime=dt_called)

    fac = utilities.HookFactory()
    reader = fac.create(type_hook='http')

    # TODO: Handle task fail, error, incomplete
    target_url = os.getenv('PERMITS_URL', None)
    headers = {"x-api-key": f"{os.getenv('PERMITS_KEY', None)}"}

    logger.info(f'Task: call endpoint {target_url}')

    # TODO: Implement input/schema verification
    try:
        with reader.loading_from(target_url=target_url,
                                 headers=headers,
                                 chunks=False) as http_data:
            sync_athena.permits_to_parquet(source_iterable=http_data,
                                           parquet_file=f"{job_id}",
                                           chunks=False,
                                           log=logger)

    except RuntimeError as e:
        logger.info(f'Task: Verify that "{target_url}" is the correct target url.')
    except BaseException as e:
        raise e

    # TODO: Implement Standard response
    return "FINISHED."


@celery.task(name='tasks.verifysourcefileexists')
def verify_source_file_exists(job_id: str):
    fac = utilities.HookFactory()
    s3_hook = fac.create(type_hook='s3').create_client(custom_region='us-east-1')
    logger.info(f"Task: s3 client: {s3_hook}")

    # sync_athena = PermitsAthena(current_uuid=job_id, s3client=s3_hook)
    # result = sync_athena.confirm_key_exist(log=True)

    object_summary = s3_hook.head_object(Bucket='flaskapi-dev-rexray-data',
                                         Key=f'data/{job_id}.parquet')

    logger.info(f"Task result: {object_summary}")
    if object_summary is not None:
        return "FINISHED."
    else:
        logger.info("Task: Key not found.")
