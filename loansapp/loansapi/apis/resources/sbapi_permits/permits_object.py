import pandas as pd

import logging

logger = logging.getLogger()


class Error(Exception):
    """Base class for exceptions in this module"""
    pass


class AthenaInitializationException(Error):
    """Exception raised for errors in SyncBQ"""
    def __init__(self, message, errors=None):
        super(AthenaInitializationException, self).__init__(str(self.__class__.__name__) + ': ' + message)
        self.errors = errors

    def __repr__(self):
        return "AthenaInitializationException"


class PermitsAthena(object):
    """
    Container for all resources and activities related for processing
    permits data from the serverlessbaseapi project.


    """
    def __init__(self, current_uuid=None):
        self.job_uuid = current_uuid

    def __repr__(self):
        # TODO: Add Athena credentials, i.e. service name, table id
        return f"aws.Athena.Client: " \
            f"'PermitsAthena.credentials'"

    def permits_to_parquet(self, source_iterable, parquet_file, chunks=False):
        """
        Saving the permits data locally (S3 mount) as parquet
        :param source_iterable: <generator object HttpHook>
        :param parquet_file: local parquet output file
        :param chunks: NOT IMPLEMENTED YET
        :return: parquet file containing report data
        """
        # PARQUET - Only in combination with S3 !!
        if not chunks:
            # ----------- 1. Run column checks--------------------------------
            # TODO: Prepare Athena Table for column check
            # checked_payload, missing_cols = self.pandas_athena_column_check(source_iterable)

            # json_data = list(checked_payload)
            json_data = list(source_iterable)[0]
            pandas_df = pd.DataFrame(json_data).reset_index().drop(columns=['index'])

            # ----------- 2. Fill missing mandatory columns with NaN values---
            # TODO: Requires Athena column check - Remove enum for no chunks
            # for enum, chunk in enumerate(checked_payload):
            #     for t in missing_cols:
            #         if t[0] == enum:
            #             for new_col in t[1]:
            #                 pandas_df[new_col] = pd.np.nan

            # ----------- 3. Map from json to pandas dtypes-------------------
            mapped_pandas_df = self.map_df_to_parquet(pandas_df)

            # ----------- 4. Save Parquet locally-----------------------------
            # TODO: Enable/test with compression snappy
            mapped_pandas_df.to_parquet(parquet_file, engine='pyarrow', compression=None)

        else:
            for _i, chunk in enumerate(source_iterable):
                # checked_chunk, missing_cols = self.pandas_athena_column_check(chunk)
                # json_data = list(checked_chunk)
                json_data = chunk
                chunk_df = pd.DataFrame(json_data).reset_index().drop(columns=['index'])
                # for enum, chunk in enumerate(checked_df):
                #     for t in missing_cols:
                #         if t[0] == enum:
                #             for new_col in t[1]:
                #                 chunk_df[new_col] = pd.np.nan
                mapped_pandas_df = self.map_df_to_parquet(chunk_df)
                mapped_pandas_df.to_parquet(f"{parquet_file}_{_i:03}.parquet", engine='pyarrow', compression=None)

    @staticmethod
    def map_df_to_parquet(df_in):
        df_map = df_in.copy(deep=True)
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
