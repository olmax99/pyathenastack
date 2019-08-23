import os
from celery import Celery


CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', None),
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', None)


celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
