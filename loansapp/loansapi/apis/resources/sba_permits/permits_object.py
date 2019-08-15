import json

import pandas as pd


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
        # TODO: Add support for chunk
        # logger.debug(f"payload_iterable {list(payload_iterable)}")
        # PARQUET - Only in combination with S3 !!
        if not chunks:
            # ----------- 1. Run column checks--------------------------------
            # TODO: Prepare Athena Table for column check
            # checked_payload, missing_cols = self.pandas_athena_column_check(source_iterable)

            # json_data = list(checked_payload)
            json_data = source_iterable
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

    @staticmethod
    def map_df_to_parquet(df_in):
        df_map = df_in.copy(deep=True)
        # df_map['column_name'] = pd.to_numeric(df_map['column_name'], downcast='float', errors='coerce')

        return df_map
