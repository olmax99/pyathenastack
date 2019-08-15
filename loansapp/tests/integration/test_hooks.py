import logging

# (chunk_size, n_rows, last_chunk)
from pathlib import Path

from loansapi.apis.resources import utilities
from tests.permits_data_generator import random_permits

test_cases = [(50, 500, 50), (20, 219, 19), (30, 20, 20)]
for i in range(len(test_cases)):
    def test_local_hook(caplog):
        """
        1. All chunks must be equal size
        2. The size of the last chunk must match (total rows % chunk size)
        3. If chunk_size is larger than number of rows then there should be
            one chunk containing all rows
        :param caplog: debugger client from pytest
        :return: A list containing the lists of all single chunks
        """
        with caplog.at_level(logging.DEBUG):
            logger = logging.getLogger()

            fac = utilities.HookFactory()
            reader = fac.create(chunk_size=test_cases[i][0])

            with open('sample_data_set.json', 'wb') as f:

                data = random_permits(n_rows=test_cases[i][1])
                # logger.debug("data_from_file: %s", data[0])
                f.write(data.encode('utf-8'))

                # Outer list containing all chunks <chain objects>
                # payload = list(reader.loading_from('sample_data_set.json', chunks=True))
                # logger.debug("payload: %s", payload)

                # Unpack the chunks <chain object> without consuming them
                with reader.loading_from('sample_data_set.json', chunks=True) as batch:
                    chunks = [list(chunk) for chunk in batch]

                    assert all(len(x) == test_cases[i][0] for x in chunks[:-1])
                    assert len(chunks[-1]) == test_cases[i][2]

            # TODO: Replace with pytest tmpfile
            Path('sample_data_set.json').unlink()
