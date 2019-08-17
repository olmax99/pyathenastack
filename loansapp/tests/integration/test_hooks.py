import logging
from itertools import chain

import pytest

from loansapi.apis.resources import utilities
from tests.permits_data_generator import random_permits


@pytest.fixture
def http_hook_no_chunks(requests_mock):
    data = random_permits(n_rows=3)
    fac = utilities.HookFactory()
    http_hook = fac.create(type_hook='http')
    requests_mock.post('http://example.com/api', text=data)
    return http_hook.loading_from(target_url='http://example.com/api',
                                  chunks=False)


@pytest.fixture
def http_hook_chunks(requests_mock):
    def _hook(chunk_size, rows):
        data = random_permits(n_rows=rows)
        fac = utilities.HookFactory()
        http_hook = fac.create(type_hook='http', chunk_size=chunk_size)
        requests_mock.post('http://example.com/api', text=data)
        return http_hook.loading_from(target_url='http://example.com/api',
                                      chunks=True)
    return _hook


test_case = [(50, 500, 50), (20, 219, 19), (30, 20, 20)]
for i in range(len(test_case)):
    def test_local_hook(caplog, tmpdir):
        """
        test_case[0]: In case of no remainder, size of first chunk is
            equal to the size of the last chunk
        test_case[1]: In case remainder exist:
            len(last chunk) = (total rows % chunk size)
        test_case[2]: If chunk_size is larger than number of rows then
            there should be one chunk containing all rows
        :param caplog: debugger client from pytest
        :return: A list containing the lists of all single chunks
        """
        with caplog.at_level(logging.DEBUG):
            logger = logging.getLogger()

            fac = utilities.HookFactory()
            reader = fac.create(chunk_size=test_case[i][0])

            # create a file test file in temp folder
            tmp_file = tmpdir.join("sample_data_set.json")

            # write randomized data to test file
            with open(tmp_file, 'wb') as f:
                data = random_permits(n_rows=test_case[i][1])
                # logger.debug("data_from_file: %s", data[0])
                f.write(data.encode('utf-8'))

            logger.debug("tmp_file: %s", tmp_file)

            # Unpack the chunks and verify test cases
            with reader.loading_from(tmp_file, chunks=True) as batch:
                chunks = [list(chunk) for chunk in batch]

                assert all(len(chunk) == test_case[i][0] for chunk in chunks[:-1])
                assert len(chunks[-1]) == test_case[i][2]

    def test_http_hook_chunks(caplog, http_hook_chunks):
        """
        Requirement: The API data has the form [{<row_1>}, ... , {<row_n>}]
        test_case[0]: In case of no remainder, size of first chunk is
            equal to the size of the last chunk
        test_case[1]: In case remainder exist:
            len(last chunk) = (total rows % chunk size)
        test_case[2]: If chunk_size is larger than number of rows then
            there should be one chunk containing all rows
        :param caplog:
        :param http_hook_chunks:
        :return:
        """
        with caplog.at_level(logging.DEBUG):
            logger = logging.getLogger()

            with http_hook_chunks(test_case[i][0], test_case[i][1]) as http_data:
                chunks = [list(chunk) for chunk in http_data]
                assert all(len(chunk) == test_case[i][0] for chunk in chunks[:-1])
                assert len(chunks[-1]) == test_case[i][2]


def test_response_form_http_hook_no_chunks(caplog, http_hook_no_chunks):
    """
    Requirement: The API data has the form [{<row_1>}, ... , {<row_n>}]
    With no chunks selected the data should be be passed on with no change,
    except the form is now [[{<row_1>}, ... , {<row_n>}]]
    1. The function loading_from() returns a nested list
    :param caplog:
    :return:
    """
    with caplog.at_level(logging.DEBUG):
        logger = logging.getLogger()

        with http_hook_no_chunks as http_data:
            logger.debug(f"data: {[row for chunk in http_data for row in chunk]}")
            assert any(isinstance(_i, list) for _i in http_data)


def test_response_form_http_hook_chunks(caplog, http_hook_chunks):
    """
    Requirement: The API data has the form [{<row_1>}, ... , {<row_n>}]
    1. The function loading_from() returns a nested list
    :param caplog:
    :param http_hook_chunks:
    :return:
    """
    with caplog.at_level(logging.DEBUG):
        logger = logging.getLogger()

        # chunk_size is not relevant here, so 10 is just chosen randomly
        with http_hook_chunks(10, 10) as http_data:
            assert any(isinstance(_i, list) for _i in http_data)
