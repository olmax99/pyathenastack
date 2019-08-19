import json
import string
import time
import pandas as pd

from datetime import timedelta, datetime
from random import randint, uniform, choice, randrange, choices


def random_time_range(start, end, file_format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formated in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, file_format))
    etime = time.mktime(time.strptime(end, file_format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(file_format, time.localtime(ptime))


def random_date(start, end):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)


def create_new_row():
    _val = [f"20160{randint(1, 9)}{randint(10, 30)}{randint(10, 24)}{randint(10, 60)}#",
            f"{random_date(datetime.strptime('1/1/2015 1:30 PM', '%m/%d/%Y %I:%M %p'), datetime.strptime('1/1/2016 4:50 AM', '%m/%d/%Y %I:%M %p'))}",
            round(uniform(33852.99, 96542), 2),
            choice([randint(0, 30), None]),
            choice(["Y", None]),
            choice([randint(0, 120), None]),
            f"{randint(94000, 94999)}{choice([f'-0000', None])}",
            None,
            None,
            f"{''.join(choices(string.ascii_uppercase, k=randint(45, 285)))}"
            ]

    _key = ["APPLICATION#", "FILE_DATE", "ESTIMATED COST", "PROPOSED UNITS", "15_DAY_HOLD?",
            "LOT", "ZIP_CODE",	"CONTACT_NAME",	"CONTACT_PHONE"	, "DESCRIPTION"]

    # This is the row creation
    return {n: m for n, m in zip(_key, _val)}


def random_permits(n_rows=2):
    return json.dumps([create_new_row() for _ in range(n_rows)])


# output = random_permits(n_rows=3)
# print(output)
# data = json.loads(output)
# print(data)
# df = pd.DataFrame(data)
# print(df.columns)


