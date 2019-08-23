import os
import uuid

from datetime import datetime
from threading import Thread

from flask import current_app
from flask_restplus import Resource
from redis import RedisError

# from loansapi.apis.resources.sbapi_permits.background_tasks import get_sba_permits
from loansapi.core.worker import celery
from loansapi.api import redis_conn


# asyncio or threading
# With asyncio endpoints needs to be called in async
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

            # Here implement the more verbose json containing all the meta data
            try:
                # TODO: Add expiration tag in redis
                redis_conn.mset({sync_runner_job_id: 'listen'})
            except RedisError as e:
                return f"Redis{e.__class__.__name__}: could not write job status '{{{sync_runner_job_id}: 'listen'}}'."

            current_app.logger.info("WebApi: Start backgroundjob.")
            # TODO: Use futures and ThreadPool or create Redis message queue
            task = celery.send_task('tasks.getsbapermits',
                                    args=[new_job_uuid, sync_runner_job_id],
                                    kwargs={})

            # Flask response standard: data or body, status code, and headers (default={'Content-Type': 'html'})
            return {'sync_runner_job_id': sync_runner_job_id,
                    'file_path': f"{os.getcwd()}/{new_job_uuid}.parquet",
                    'job_description': 'serverlessbaseapi Permits data',
                    'called_at': str(called_at),
                    }, 201, {'Content-Type': 'application/json'}
