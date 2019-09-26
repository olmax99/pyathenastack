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
def update_partition(job_id: str, partition_name: str) -> Optional[str]:
    fac = utilities.HookFactory()
    glue_hook = fac.create(type_hook='glue').create_client(custom_region='eu-central-1')

    sync_athena = PermitsAthena(current_uuid=job_id)
    # -------------------- STEP 1: Verify that partition does not exist-----------------------------
    get_part_info = None
    try:
        get_glue_part_r = glue_hook.get_partition(DatabaseName=sync_athena.permits_database,
                                                  TableName=sync_athena.permits_table,
                                                  # PartitionValues=['2019-09-07'])
                                                  PartitionValues=[f"{partition_name}"])
        get_part_info = get_glue_part_r
        # logger.info(f"partition_name: {partition_name}, glue_partition: {get_glue_part_r}")
    except ClientError as e:
        logger.info(f"message: partitiontime='{partition_name}' not found. Create new partition '{partition_name}'")
        if 'GetPartition operation: Cannot find partition.' in str(e):
            # ------------- STEP 2: Parsing table info required to create partitions from table----
            table_info = None
            try:
                glue_tbl_r = glue_hook.get_table(DatabaseName=sync_athena.permits_database,
                                                 Name=sync_athena.permits_table)
                # logger.info(f"glue_table: {glue_tbl_r}")
            except ClientError as e:
                table_info = {'error': e}
                return f"{table_info}"
            else:
                try:
                    part_input_dict = {'Values': [f'{partition_name}'],
                                       'StorageDescriptor': {
                                           'Location': f"{glue_tbl_r['Table']['StorageDescriptor']['Location']}/partitiontime={partition_name}/",
                                           'InputFormat': glue_tbl_r['Table']['StorageDescriptor']['InputFormat'],
                                           'OutputFormat': glue_tbl_r['Table']['StorageDescriptor']['OutputFormat'],
                                           'SerdeInfo': glue_tbl_r['Table']['StorageDescriptor']['SerdeInfo']
                                       }}
                    # partition_keys = glue_tbl_r['Table']['PartitionKeys']
                except KeyError as e:
                    table_info = {'error': e, 'message': 'Could not retrieve Keys from Glue::Table.'}
                except BaseException as e:
                    table_info = {'error': 'Unexpected error', 'message': e}
                else:
                    # ------- STEP 3: Create new partition----------------------------------------
                    try:
                        create_glue_part_r = glue_hook.create_partition(DatabaseName=sync_athena.permits_database,
                                                                        TableName=sync_athena.permits_table,
                                                                        PartitionInput=part_input_dict)
                    except ClientError as e:
                        table_info = {'error': 'Unexpected error when creating partition', 'message': e}
                    except BotoCoreError as e:
                        logger.info(f"Unknown BotoCoreError: {e}")
                        table_info = {'error': e}
                    else:
                        # logger.info(f'message: {create_glue_part_r}')
                        get_part_info = create_glue_part_r
                finally:
                    if table_info is not None:
                        return f"{table_info}"
    except BotoCoreError as e:
        logger.info(f"Unknown BotoCoreError: {e}")
        get_part_info = {'error': e}
    finally:
        return f"{get_part_info}"


# def copy_src_f_to_partition():
    # f"Copy 's3://{sync_athena.base_data_store}{job_id}.parquet' to" \
    # f"s3://{sync_athena.base_data_store} with " \
    # f"Glue::{sync_athena.permits_database}.{sync_athena.permits_table}.partitiontime='{partition_name}'."
