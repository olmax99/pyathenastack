import json
import os
import uuid

from datetime import datetime

from flask import current_app
from flask_restplus import Namespace, Resource

from flaskapi.core.worker import celery
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


@ns.route('/data_store/<job_id>')
@ns.doc(params={'job_id': 'Unique uuid - file needs to exist.'})
class PermitsDataStore(Resource):
    def post(self, job_id):
        """
        Copy source file from data lake to data store partition.
        :param job_id:
        :return:
        """
        with current_app.app_context():
            called_at = datetime.utcnow()
            target_partition = str(called_at.date())
            new_job_uuid = str(uuid.uuid1())

            current_app.logger.info(f'WebApi: create new job_id {new_job_uuid} for "Copy source file to Data Store".')
            # STEP 1: Verify that file exists in s3
            task = celery.send_task('tasks.verifysourcefileexists',
                                    args=[job_id],
                                    kwargs={})
            # try:
            current_app.logger.info(f"task_id: {task.id}")
            res = celery.AsyncResult(id=task.id)
            res.wait(4)
            result = res.get(timeout=5) if (res.state == 'SUCCESS') or \
                                           (res.state == 'FAILURE') else None
            # except celery.exceptions.TimeoutError as e:
            #     current_app.logger.info(f"WebApi: Could not get result in time.\n {e}.")
            # except BaseException as e:
            #     current_app.logger.info(f"WebApi: Unexpected error.\n {e}.")

            # Run background task
            # Create boto3 glue conn
            # 1. Verify that target partition exists
            # 2. If not exist, create partition
            # 3. Move file to partition
            # Use chaining

            return {'sync_runner_job_id': new_job_uuid,
                    'target_partition': f"/partitiontime='{target_partition}'",
                    'source_file_path': f'/{job_id}.parquet',
                    'source_file_found': f'{result}',
                    'called_at': str(called_at),
                    }, 201, {'Content-Type': 'application/json'}
