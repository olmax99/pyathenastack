import io
import logging
import contextlib

import ijson
import requests

from requests.auth import HTTPBasicAuth
from itertools import chain, islice


logger = logging.getLogger()


class BaseHook(object):
    def __repr__(self):
        return "BaseHook"

    def __init__(self, chunk_size):
        self._size = chunk_size

    @contextlib.contextmanager
    def loading_from(self, *args, **kwargs):
        pass

    def _chunks(self, iterable_object):
        _it = iter(iterable_object)
        for start in _it:
            yield list(chain([start], islice(_it, self._size - 1)))


class LocalHook(BaseHook):
    def __repr__(self):
        return f"LocalHook(chunk_size={self._size}"

    @contextlib.contextmanager
    def loading_from(self, source_path, chunks=True, custom_encoding='utf-8', mapper=None):
        with open(source_path, 'r', encoding=custom_encoding) as file:
            mapped_gen = (row for row in map(mapper, ijson.items(file=file, prefix='item')))
            logger.debug(f"mapped_gen = {mapped_gen}")
            if not chunks:
                yield mapped_gen
            else:
                yield self._chunks(iterable_object=mapped_gen)


class HttpHook(BaseHook):
    def __repr__(self):
        return f"HttpHook(chunk_size={self._size})"

    @contextlib.contextmanager
    def loading_from(self, target_url,
                     headers=None,
                     user_name=None, user_password=None,
                     chunks=True,
                     custom_encoding='utf-8'):
        try:
            with requests.post(target_url,
                               headers=headers,
                               auth=HTTPBasicAuth(user_name, user_password),
                               timeout=10,
                               stream=True) as r:
                r.encoding = custom_encoding
                if not chunks:
                    # encoding only works on response text object
                    yield (row for row in ijson.items(io.StringIO(r.text), 'item'))
                else:
                    yield self._chunks(
                        row for row in ijson.items(io.StringIO(r.text), 'item'))
        except requests.exceptions.HTTPError as e:
            logger.log(logging.DEBUG, f"{e}")
        except requests.exceptions.RequestException as e:
            logger.log(logging.DEBUG, f"{e}")
