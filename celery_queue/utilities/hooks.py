import io
import logging
import contextlib
import os

import boto3 as boto3
import ijson
import requests

# from requests.auth import HTTPBasicAuth
from itertools import chain, islice

from botocore.exceptions import ClientError, ProfileNotFound

logger = logging.getLogger()


class BaseHook(object):
    def __init__(self, chunk_size=None):
        self._size = chunk_size

    def __repr__(self):
        return "BaseHook"

    def create_conn(self):
        pass

    @contextlib.contextmanager
    def loading_from(self, *args, **kwargs):
        pass

    def _chunks(self, iterable_object):
        _it = iter(iterable_object)
        for start in _it:
            yield list(chain([start], islice(_it, self._size - 1)))


# Currently not used, since http stream will save parquet file to folder,
# which is mounted to an S3
class LocalHook(BaseHook):
    def __init__(self, chunk_size):
        super(LocalHook, self).__init__(chunk_size=chunk_size)

    def __repr__(self):
        return f"LocalHook(chunk_size={self._size}"

    @contextlib.contextmanager
    def loading_from(self, source_path, chunks=True, custom_encoding='utf-8'):
        with open(source_path, 'r', encoding=custom_encoding) as file:
            source_gen = (row for row in ijson.items(file=file, prefix='item'))
            logger.debug(f"source_gen = {source_gen}")
            if not chunks:
                yield source_gen
            else:
                yield self._chunks(iterable_object=source_gen)


class HttpHook(BaseHook):
    def __init__(self, chunk_size):
        super(HttpHook, self).__init__(chunk_size=chunk_size)

    def __repr__(self):
        return f"HttpHook(chunk_size={self._size})"

    @contextlib.contextmanager
    def loading_from(self, target_url,
                     headers=None,
                     # user_name=None, user_password=None,
                     chunks=True,
                     custom_encoding='utf-8'):
        try:
            with requests.post(target_url,
                               headers=headers,
                               # auth=HTTPBasicAuth(user_name, user_password),
                               timeout=100,
                               stream=True) as r:
                r.encoding = custom_encoding
                if not chunks:
                    # encoding only works on response text object
                    yield [[row for row in ijson.items(io.StringIO(r.text), 'item')]]
                else:
                    yield self._chunks(
                        row for row in ijson.items(io.StringIO(r.text), 'item'))
        except requests.exceptions.HTTPError as e:
            logger.log(logging.DEBUG, f"{e}")
        except requests.exceptions.RequestException as e:
            logger.log(logging.DEBUG, f"{e}")


class S3Hook(BaseHook):
    def __init__(self):
        super(S3Hook, self).__init__()
        self.aws_access_id = os.getenv('AWS_ACCESS_KEY_ID', None)
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY', None)
        self._session = None

    def __repr__(self):
        return f"S3Hook"

    def create_client(self, custom_region=None):
        try:
            self._session = boto3.Session(aws_access_key_id=self.aws_access_id,
                                          aws_secret_access_key=self.aws_secret_key)
        except ClientError:
            logger.log(logging.DEBUG, f"FATAL. Could not create s3 client session")
        else:
            if custom_region is not None:
                s3_client = self._session.client('s3', region_name=f"{custom_region}")
            else:
                s3_client = self._session.client('s3')
            return s3_client


class CfnHook(BaseHook):
    def __init__(self):
        super(CfnHook, self).__init__()
        self.aws_access_id = os.getenv('AWS_ACCESS_KEY_ID', None)
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY', None)
        self._session = None

    def create_client(self, custom_region=None):
        try:
            self._session = boto3.Session(aws_access_key_id=self.aws_access_id,
                                          aws_secret_access_key=self.aws_secret_key)
        except ClientError:
            logger.log(logging.DEBUG, f"FATAL. Could not create cloudformation client session")
        else:
            if custom_region is not None:
                cfn_client = self._session.client('cloudformation', region_name=f"{custom_region}")
            else:
                cfn_client = self._session.client('cloudformation')
            return cfn_client


class GlueHook(BaseHook):
    def __init__(self):
        super(GlueHook, self).__init__()
        self.aws_access_id = os.getenv('AWS_ACCESS_KEY_ID', None)
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY', None)
        self._session = None

    def create_client(self, custom_region=None):
        try:
            self._session = boto3.Session(aws_access_key_id=self.aws_access_id,
                                          aws_secret_access_key=self.aws_secret_key)
        except ClientError:
            logger.log(logging.DEBUG, f"FATAL. Could not establish glue client session")
        else:
            if custom_region is not None:
                glue_client = self._session.client('glue', region_name=f"{custom_region}")
            else:
                glue_client = self._session.client('glue')
            return glue_client
