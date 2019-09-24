import os

from typing import Optional

from botocore.exceptions import ClientError, BotoCoreError
from celery import Celery, group
from celery.utils.log import get_task_logger
from botocore.exceptions import ValidationError

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


# TODO: Add schema verification for input variables
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
def verify_source_file_exists(job_id: str) -> Optional[str]:
    fac = utilities.HookFactory()
    s3_hook = fac.create(type_hook='s3').create_client(custom_region='us-east-1')
    # logger.info(f"Task: s3 client: {s3_hook}")

    sync_athena = PermitsAthena(current_uuid=job_id)

    # TODO: Move to PermitsAthena class object
    object_summary = None
    try:
        object_summary = s3_hook.head_object(Bucket=sync_athena.base_bucket,
                                             Key=f'data/{job_id}.parquet')
    except ClientError as e:
        if e.response['Error']['Code'] == '404' and 'HeadObject operation: Not Found' in str(e):
            # logger.info("HEAD object not found.")
            object_summary = {'error': e, 'e.response': e.response['Error']}
        else:
            logger.info(f"Unknown ClientError: {e, e.response['Error']}")
            object_summary = {'error': e, 'e.response': e.response['Error']}
    except BotoCoreError as e:
        logger.info(f"Unknown BotoCoreError: {e}")
        object_summary = {'error': e}
    finally:
        if object_summary is not None:
            return f"{object_summary}"
        else:
            return object_summary


@celery.task(name='tasks.verifytargetstackexists')
def verify_target_stack_exists(stack_name: str) -> Optional[str]:
    fac = utilities.HookFactory()
    cfn_hook = fac.create(type_hook='cfn').create_client(custom_region='eu-central-1')

    # TODO: Move to PermitsAthena class object
    cfn_summary = None
    try:
        cfn_summary = cfn_hook.get_template_summary(StackName=stack_name)
        logger.info(f'cfn_template_summary: {cfn_summary}')
    except ClientError as e:
        logger.info(f'error: {e}'
                    f'error_response: {e.response}')
        if e.response['Error']['Code'] == 'ValidationError' and 'does not exist' in e.response['Error']['Message']:
            cfn_summary = {'error': e, 'e.response': e.response['Error']}
        else:
            logger.info(f"Unknown ClientError: {e, e.response['Error']}")
            cfn_summary = {'error': e, 'e.response': e.response['Error']}
    except BotoCoreError as e:
        logger.info(f"Unknown BotoCoreError: {e}")
        cfn_summary = {'error': e}
    else:
        req_resources = ['AWS::S3::Bucket', 'AWS::Glue::Database', 'AWS::Glue::Table', 'AWS::Glue::Partition']
        if not all(item in req_resources for item in cfn_summary['ResourceTypes']):
            cfn_summary = {'error': 'CustomValidationError',
                           'e.response': 'Stack resources do not fulfill the requirements.'}
    finally:
        if cfn_summary is not None:
            return f"{cfn_summary}"
        else:
            return cfn_summary


@celery.task(name='tasks.updatepartition')
def update_partition():
    pass
