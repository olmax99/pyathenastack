import json
import os
import uuid

from datetime import datetime

from flask import current_app
from flask_restplus import Namespace, Resource
# from celery import group

from flaskapi.core.worker import celery
from celery.exceptions import TimeoutError, CeleryError
from celery import group
# from flaskapi.api import redis_conn

ns = Namespace('permits', description='A sample of SF housing permits')


# TODO: Schema and request status handling (including exceptions!!)
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
        :return: Copying source file into partition will only take place if both are identified.
        """
        with current_app.app_context():
            called_at = datetime.utcnow()
            target_partition = str(called_at.date())
            new_job_uuid = str(uuid.uuid1())

            current_app.logger.info(f'WebApi: create new job_id {new_job_uuid} for "Copy source file to Data Store".')

            # --------------------- STEP 1: Verify source file and target stack exist----------------
            verify_src_s = celery.signature('tasks.verifysourcefileexists', args=(job_id,), kwargs={}, options={})
            verify_stack_s = celery.signature('tasks.verifytargetstackexists', args=(stack_name,),
                                              kwargs={}, options={})
            # Run in parallel
            res_verify_grp = group(verify_src_s, verify_stack_s)()
            try:
                # current_app.logger.info(f"GroupResult: {res_verify_grp.results}")
                result_collect = [(i.id, i.get()) for i in res_verify_grp.results]
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
            # update_part_s = celery.signature('tasks.updatepartition', args=(job_id, target_partition,), kwargs={}, options={})
            res_update_part = celery.send_task('tasks.updatepartition', args=[job_id, target_partition],
                                               kwargs={})
            try:
                res = celery.AsyncResult(id=res_update_part.id)
                # res.wait(4)
            except CeleryError as e:
                current_app.logger.info(f"WebApi: Unexpected error.{e}.")

            # CHAIN: DEPENDS ON STEP 2
            # STEP 3: Copy source file to target partition
            # 4. Move file to new or existing partition

            return {'sync_runner_job_id': new_job_uuid,
                    'result_grp': f"{result_collect}",
                    # 'source_file': f'{result_src_f}',
                    # 'data_store': f'{result_stack}',
                    'called_at': str(called_at),
                    }, 201, {'Content-Type': 'application/json'}
