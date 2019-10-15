FROM python:3.6.9-slim-stretch

# RUN apk update
# RUN apk add make automake gcc g++ subversion python3-dev

COPY ./ /queue
WORKDIR /queue

RUN pip install -r requirements.txt

ENTRYPOINT celery -A tasks worker --loglevel=INFO
