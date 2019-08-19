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


def mock_map_df(df_in):
    df_map = df_in.copy(deep=True)
    # Column name mapping
    df_map.rename(columns={'APPLICATION#': 'application_id',
                           'FILE_DATE': 'file_date',
                           'ESTIMATED COST': 'est_cost',
                           'PROPOSED UNITS': 'proposed_units',
                           '15_DAY_HOLD?': 'days_hold_15',
                           'LOT': 'estate_lot',
                           'ZIP_CODE': 'estate_zip_code',
                           'CONTACT_NAME': 'agent_name',
                           'CONTACT_PHONE': 'agent_phone',
                           'DESCRIPTION': 'estate_description'},
                  inplace=True)

    # Type mapping
    df_map['application_id'] = df_map['application_id'].astype('str', errors='ignore').replace('nan', pd.np.nan)
    df_map['file_date'] = pd.to_datetime(df_map['file_date'], errors='coerce').dt.date
    df_map['est_cost'] = pd.to_numeric(df_map['est_cost'], downcast='float', errors='coerce')
    df_map['proposed_units'] = pd.to_numeric(df_map['proposed_units'], downcast='integer', errors='coerce')
    df_map['days_hold_15'] = df_map['days_hold_15'].astype('bool')
    df_map['estate_lot'] = pd.to_numeric(df_map['estate_lot'], downcast='integer', errors='coerce')
    df_map['estate_zip_code'] = df_map['estate_zip_code'].astype('str', errors='raise').replace('nan', pd.np.nan)
    df_map['agent_name'] = df_map['agent_name'].astype('str', errors='raise').replace('nan', pd.np.nan)
    df_map['agent_phone'] = df_map['agent_phone'].astype('str', errors='raise').replace('nan', pd.np.nan)
    df_map['estate_description'] = df_map['estate_description'].astype('str', errors='raise').replace('nan', pd.np.nan)
    return df_map


def test_write_parquet_file_no_chunks(caplog,
                                      mocker,
                                      tmpdir,
                                      http_hook_no_chunks):
    with caplog.at_level(logging.DEBUG):
        logger = logging.getLogger()

        # create a file test file in temp folder
        tmp_file = tmpdir.join("sample_data_set.parquet")

        with http_hook_no_chunks as http_stream:
            df_generated = pd.DataFrame(http_stream[0]).reset_index().drop(columns=['index'])
            # logger.debug(f"df_generated: \n {df_generated}")

            mocked_map_df_to_parquet = mocker.patch.object(PermitsAthena, 'map_df_to_parquet')
            mocked_map_df_to_parquet.return_value = mock_map_df(df_generated)

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
