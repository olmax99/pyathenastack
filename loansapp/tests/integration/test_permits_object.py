import itertools
import json
import logging

import pytest
import pandas as pd

from loansapi.apis.resources import utilities
from loansapi.apis.resources.sbapi_permits.permits_object import PermitsAthena
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


def test_permits_to_parquet_no_chunks(caplog,
                                      tmpdir,
                                      http_hook_no_chunks):
    with caplog.at_level(logging.DEBUG):
        logger = logging.getLogger()

        # create a file test file in temp folder
        tmp_file = tmpdir.join("sample_data_set.parquet")

        with http_hook_no_chunks as http_stream:
            df_generated = pd.DataFrame(http_stream[0]).reset_index().drop(columns=['index'])
            # logger.debug(f"df_generated: \n {df_generated}")

            permits_object = PermitsAthena()
            permits_object.permits_to_parquet(source_iterable=http_stream,
                                              parquet_file=tmp_file,
                                              chunks=False)

        test_parquet_df = pd.read_parquet(path=tmp_file,
                                          engine='pyarrow')

        logger.debug(f"parquet_df: {test_parquet_df}")
        logger.debug(f"parquet_df: {df_generated}")

        # df_generated['ESTIMATED COST'].sum() will come as type Decimal()
        df_generated['ESTIMATED COST'] = pd.to_numeric(df_generated['ESTIMATED COST'], downcast='float', errors='coerce')

        assert test_parquet_df['est_cost'].sum() == \
            df_generated['ESTIMATED COST'].sum()


# TODO: test cases with unequal chunks
test_case = [(3, 9)]
for _c in test_case:
    def test_permits_to_parquet_chunks(caplog, tmpdir, http_hook_chunks):
        with caplog.at_level(logging.DEBUG):
            logger = logging.getLogger()

            # create a file test file in temp folder
            tmp_file = tmpdir.join("sample_data_chunk")

            with http_hook_chunks(_c[0], _c[1]) as http_stream_chunks:
                logging.debug(f"http_stream_chunks: {http_stream_chunks}")
                http_gen, http_gen_copy = itertools.tee(http_stream_chunks, 2)
                # ------------------Generate expected data ----------------------------
                df_generated = pd.DataFrame
                for enum, chunk in enumerate(http_gen_copy):
                    # logger.debug(f"list(chunk): \n {list(chunk)}")
                    df_generated_chunk = pd.DataFrame(list(chunk)).reset_index().drop(columns=['index'])
                    if not df_generated.empty:
                        df_generated = df_generated.append(df_generated_chunk)
                    else:
                        df_generated = df_generated_chunk
                # logger.debug(f"df_generated: \n {df_generated}")

                # -------------------Run target function ------------------------------
                permits_object = PermitsAthena()
                permits_object.permits_to_parquet(source_iterable=http_gen,
                                                  parquet_file=tmp_file,
                                                  chunks=True)
                logger.debug(f"tmp_dir: {tmpdir.listdir()}")

            # ---------------------Test if target parquet exists and read output ------------------------
            test_parquet_df_000 = pd.read_parquet(path=f"{tmp_file}_000.parquet", engine='pyarrow')
            test_parquet_df_001 = pd.read_parquet(path=f"{tmp_file}_001.parquet", engine='pyarrow')
            test_parquet_df_002 = pd.read_parquet(path=f"{tmp_file}_002.parquet", engine='pyarrow')

            # logger.debug(f"test_parquet_df_000: {test_parquet_df_000[['application_id', 'est_cost']]} \n"
            #              f" {df_generated[['APPLICATION#', 'ESTIMATED COST']].iloc[:3]}")
            df_generated['ESTIMATED COST'] = pd.to_numeric(df_generated['ESTIMATED COST'], downcast='float', errors='coerce')

            assert test_parquet_df_000['est_cost'].sum() == df_generated['ESTIMATED COST'].iloc[:3].sum()
            assert test_parquet_df_001['est_cost'].sum() == df_generated['ESTIMATED COST'].iloc[3:6].sum()
            assert test_parquet_df_002['est_cost'].sum() == df_generated['ESTIMATED COST'].iloc[6:].sum()

