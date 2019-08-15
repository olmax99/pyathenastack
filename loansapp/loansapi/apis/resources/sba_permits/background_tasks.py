import os

from redis import RedisError

from loansapi.api import redis_conn


def get_sba_permits(uwsgi_app_object, job_id, long_job_id):
    from loansapi.apis.resources.sba_permits.permits_object import PermitsAthena
    sync_athena = PermitsAthena(current_uuid=job_id)

    from loansapi.apis.resources import utilities
    fac = utilities.HookFactory()
    reader = fac.create(type_hook='http', chunk_size=2)

    redis_conn.set(long_job_id, 'active')
    uwsgi_app_object.logger.info('WebApi: job started "get sba-permits"')

    target_url = os.getenv('PERMITS_URL')
    headers = {"x-api-key": f"{os.getenv('PERMITS_KEY')}"}

    # TODO: Unpack <chunk chain objects> without using list
    # Run download and write file
    with reader.loading_from(target_url=target_url,
                             headers=headers,
                             chunks=False) as http_data:

        sync_athena.permits_to_parquet(source_iterable=http_data, parquet_file=f"{job_id}.parquet")

    # use consistent methods with redis: mset or set
    try:
        redis_conn.set(long_job_id, 'finished')
    except RedisError as e:
        print(f"{e.__class__.__name__}: could not write job status '{{{job_id}: 'finished'}}'.")

    uwsgi_app_object.logger.info(f"WebApi: get sba-permits finished - '{job_id}'")
