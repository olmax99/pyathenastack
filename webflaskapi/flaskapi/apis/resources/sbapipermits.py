import json
import os
import uuid

from datetime import datetime

from flask import current_app
from flask_restplus import Namespace, Resource

from flaskapi.core.worker import celery
from celery.exceptions import TimeoutError, CeleryError
# from flaskapi.api import redis_conn

ns = Namespace('permits', description='A sample of SF housing permits')


# TODO: Schema and request status handling (including exceptions!!
@ns.route('/report', endpoint='report')
class PermitsReport(Resource):
    def get(self):
        """
        This is the download of all Permits data exposed through the serverlessbaseapi
        :return: <current job meta data>, response.code, response.header
        """

        with current_app.app_context():
            called_at = datetime.utcnow()
            new_job_uuid = str(uuid.uuid1())
            sync_runner_job_id = f"permits_{new_job_uuid}"

            current_app.logger.info(f'WebApi: create new job_id "{sync_runner_job_id}" for "Get Permit Report".')

            res = celery.send_task('tasks.getsbapermits',
                                   args=[new_job_uuid, sync_runner_job_id, called_at],
                                   kwargs={})

            current_app.logger.info(f"WebApi: Start background job with id {res.id}.")

            # TODO: Use generic response implementation
            # Flask response standard: data or body, status code, and headers (default={'Content-Type': 'html'})
            return {'sync_runner_job_id': sync_runner_job_id,
                    'task': res.id,
                    'file_path': f"{os.getcwd()}/data/{new_job_uuid}.parquet",
                    'job_description': 'serverlessbaseapi Permits data',
                    'called_at': str(called_at),
                    }, 201, {'Content-Type': 'application/json'}


@ns.route('/<task_id>')
@ns.doc(params={'task_id': 'An ID'})
class PermitsStateCheck(Resource):
    def post(self, task_id):
        """
        Check the current state of a celery background task.
        TODO: result.forget() is required, but conflicts with idempotency
        :return:
        """
        with current_app.app_context():
            res = celery.AsyncResult(id=task_id)
            result = res.get(timeout=2) if (res.state == 'SUCCESS') or \
                                           (res.state == 'FAILURE') else None

            return {"state": f"{res.state}",
                    "result": f"{result}"
                    }, 201, {'Content-Type': 'application/json'}


@ns.route('/to_data_store/<job_id>/<stack_name>')
@ns.doc(params={'job_id': 'Unique job uuid - file needs to exist.',
                'stack_name': 'Athena stack containing S3 data sore, Glue db, table, and partition'})
class PermitsToDataStore(Resource):
    def post(self, job_id, stack_name):
        """
        Copy source file from data lake to data store partition.
        :param job_id: Uuid of source file, which need to exist in data lake bucket.
        :param stack_name: Name of the Athena target stack, which is required to contain the following resources:
        'AWS::S3::Bucket', 'AWS::Glue::Database', 'AWS::Glue::Table', 'AWS::Glue::Partition'
        :return: Verification of source and target. Copying of source file into target partition will take place if
        both are successfully located. The Background task will not execute if either source or target has an error.
        """
        with current_app.app_context():
            called_at = datetime.utcnow()
            target_partition = str(called_at.date())
            new_job_uuid = str(uuid.uuid1())

            current_app.logger.info(f'WebApi: create new job_id {new_job_uuid} for "Copy source file to Data Store".')

            # --------------------- STEP 1: Verify source file and target stack exist----------------

            # 1. Verify that source file exists
            task_src = celery.send_task('tasks.verifysourcefileexists', args=[job_id], kwargs={})
            # 2. Verify that target stack/table/partition exists
            task_stack = celery.send_task('tasks.verifytargetstackexists', args=[stack_name, target_partition],
                                          kwargs={})
            try:
                # current_app.logger.info(f"task_id: {task.id}")
                res_src = celery.AsyncResult(id=task_src.id)
                res_src.wait(4)
                res_stack = celery.AsyncResult(id=task_stack.id)
                res_stack.wait(4)
                result_src_f = res_src.get(timeout=5) if (res_src.state == 'SUCCESS') or \
                                                         (res_src.state == 'FAILURE') else None
                result_stack = res_stack.get(timeout=5) if (res_src.state == 'SUCCESS') or \
                                                           (res_src.state == 'FAILURE') else None
            except TimeoutError as e:
                current_app.logger.info(f"WebApi: Could not get result in time. TimeoutError: {e}.")
            except CeleryError as e:
                current_app.logger.info(f"WebApi: Unexpected error.{e}.")

            # --------------------- STEP 2: Update stack---------------------------------------------
            #    Chain: Depends on task_src AND task_stack from STEP 1
            #    Verify head_object and target stack resources are valid
            # ---------------------------------------------------------------------------------------

            # 2. If not exist, create new partition
            # 3. Update stack

            # CHAIN: DEPENDS ON STEP 2
            # STEP 3: Copy source file to target partition
            # 4. Move file to new or existing partition

            return {'sync_runner_job_id': new_job_uuid,
                    'source_file': f'{result_src_f}',
                    'data_store': f'{result_stack}',
                    'called_at': str(called_at),
                    }, 201, {'Content-Type': 'application/json'}
