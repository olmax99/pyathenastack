# import os
#
# from redis import RedisError
#
# from loansapi.api import redis_conn
#
#
# # TODO: Verify if app.logger is necessary or replace by custom task logger
# #  i.e. from celery_queue.utils.log import get_task_logger
# #  logger = get_task_logger(__name__)
# def get_sba_permits(uwsgi_app_object, job_id: str, long_job_id: str):
#     from loansapi.apis.resources.sbapi_permits.permits_object import PermitsAthena
#     sync_athena = PermitsAthena(current_uuid=job_id)
#
#     from loansapi.apis.resources import utilities
#     fac = utilities.HookFactory()
#     reader = fac.create(type_hook='http', chunk_size=200)
#
#     try:
#         redis_conn.set(long_job_id, 'active')
#     except RedisError as e:
#         print(f"Redis{e.__class__.__name__}: could not write job status '{{{job_id}: 'active'}}'.")
#
#     uwsgi_app_object.logger.info('WebApi: job started "get sba-permits"')
#
#     target_url = os.getenv('PERMITS_URL', None)
#     headers = {"x-api-key": f"{os.getenv('PERMITS_KEY', None)}"}
#
#     # Run download and write file
#     with reader.loading_from(target_url=target_url,
#                              headers=headers,
#                              chunks=False) as http_data:
#
#         sync_athena.permits_to_parquet(source_iterable=http_data, parquet_file=f"{job_id}", chunks=False)
#
#     try:
#         redis_conn.set(long_job_id, 'finished')
#     except RedisError as e:
#         print(f"Redis{e.__class__.__name__}: could not write job status '{{{job_id}: 'finished'}}'.")
#
#     uwsgi_app_object.logger.info(f"WebApi: get sba-permits finished - '{job_id}'")
