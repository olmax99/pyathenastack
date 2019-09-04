import os
import uuid

from datetime import datetime

from flask import current_app
from flask_restplus import Resource
# from redis import RedisError


from flaskapi.core.worker import celery
# from flaskapi.api import redis_conn


class PermitsReport(Resource):
    def post(self):
        """
        This is the download of all Permits data exposed through the serverlessbaseapi
        :return: <current job meta data>, response.code, response.header
        """

        with current_app.app_context():
            called_at = datetime.utcnow()
            new_job_uuid = str(uuid.uuid1())
            sync_runner_job_id = f"permits_{new_job_uuid}"

            current_app.logger.info(f'WebApi: create new job_id "{sync_runner_job_id}"')

            task = celery.send_task('tasks.getsbapermits',
                                    args=[new_job_uuid, sync_runner_job_id, called_at],
                                    kwargs={})

            current_app.logger.info(f"WebApi: Start background job with id {task.id}.")

            # TODO: Use generic response implementation
            # Flask response standard: data or body, status code, and headers (default={'Content-Type': 'html'})
            return {'sync_runner_job_id': sync_runner_job_id,
                    'task': task.id,
                    'file_path': f"{os.getcwd()}/data/{new_job_uuid}.parquet",
                    'job_description': 'serverlessbaseapi Permits data',
                    'called_at': str(called_at),
                    }, 201, {'Content-Type': 'application/json'}
