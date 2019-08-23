# Docker Flask API [![Build Status](https://travis-ci.org//olmax99/dockerflaskapi.png)](https://travis-ci.org//olmax99/dockerflaskapi)

This is a web API project. Its main purpose is to store large datasets
into a data lake (AWS S3), and further load the data into the data 
warehouse (AWS Athena).

The application can be deployed anywhere Docker can be deployed to. 
Tests are performed using the pytest framework. The ORM is set up in 
SQLAlchemy directly applying the flask declarative base approach.

--- 

**Project Design**

- Store large JSON to parquet.
- celery + redis background worker
- session token with user id (postgres)
- alembic database updates
- persistent logs (postgres)
- JWT passphrase endpoints
- cloudformation.staging.yml + cloudformation.production.yml
- Review 'AWS Well Architected Framework' - split templates into VPC groups
- Admin view for creating users and store JWT

![Graph](images/dockerflaskapi.png)

## Prerequisites

+ Pyenv
+ Pipenv integrated with Pyenv
+ Python Version 3.7.1
+ Docker installed [official Docker docs](https://docs.docker.com/)

---

**NOTE:** Currently, Celery will fail on Python 3.7.1 due to conflicting naming
of packages using `async`, which is now a keyword in Python. Downgrade to `3.6.9`


## Quickstart

---

**NOTE:** For demonstration purposes, this project assumes the [serverless base api](https://github.com/olmax99/serverlessbaseapi) 
project as the data source and to be up and running.

### 1. Preparing the project environment

In the directory  `dockerflaskapi/loansapp`:

```
$ pipenv install
$ pipenv shell

(loansapp)$ pipenv install Flask
(loansapp)$ pipenv install flask-restplus
(loansapp)$ pipenv install flask-redis
(loansapp)$ pipenv install sqlalchemy
(loansapp)$ pipenv install psycopg2
(loansapp)$ pipenv install pytest


```

In PyCharm:

In PyCharm > Settings > Project Interpreter:
+ Verify that the Project Interpreter `Pipenv(loansapp)` is selected.

*NOTE:*   PyCharm should be opened with the loansapp directory as the
  top folder. Otherwise the pipenv interpreter might behave in an 
  unexpected way.

In PyCharm > Tools > Python Integrated Tools > Testing

+ Set default test runner: pytest

*NOTE:*   Installing from PyCharm or even from both terminal and 
  PyCharm should make no difference. Ensure that *Pipfile.lock* is 
  up-to-date. In Pipfile directory simply run `$ pipenv lock` for 
  creating a new `Pipfile.lock`.


### 2. Create the database credential files

There are two files containing the database access credentials that 
need to be created manually.

From the terminal:

**NOTE:** All values provided here need to match the values provided in
the `.env` file.

Inside the `dockerflaskapi` directory:

```
$ vim .env.web.dev

# parameters need to match with those of .env file
POSTGRES_URI=postgres+psycopg2://flask:super_secret@postgres.flaskapi/flask_api
REDIS_URI=redis://:super_secret2@redis.flaskapi:6379/0
CELERY_BROKER_URL=redis://:super_secret2@redis.flaskapi:6379/0
CELERY_RESULT_BACKEND=redis://:super_secret2@redis.flaskapi:6379/0
PERMITS_URL=<cf-apigateway>                               <-- Get from 'serverless base api' project
PERMITS_KEY=<x-api-key>                                   <-- Get from 'serverless base api' project

$ vim .env.worker.dev

CELERY_BROKER_URL=redis://:super_secret2@redis.flaskapi:6379/0
CELERY_RESULT_BACKEND=redis://:super_secret2@redis.flaskapi:6379/0

$ vim .env

DEV_DB=flask_api
DEV_USER=flask
DEV_PASSWORD=super_secret
REDIS_PASSWD=super_secret2
REDIS_URI=redis://:super_secret2@redis.flaskapi:6379/0

```

### 3. Run the project

#### 1. Set the applications run mode

There are two ways of running the app in development mode. By default 
the `web` container will run in sleep, and flask is invoked in debug.

1. If you want to run the Flask app directly from nginx/uwsgi, comment 
out the line starting with `command: ...` in 
`dockerflaskapi/docker-compose.development.yml`:

```
# command: pipenv run flask run --host=0.0.0.0 --port=5000
# Infinite loop, to keep it alive, for debugging
# command: bash -c "while true; do echo 'sleeping...' && sleep 10; done"  <-- COMMENT OUT

```

2. If you want to run the application in DEBUG mode for developing on the
code base, uncomment the last line. It is then recommended to run docker 
in detached mode

#### 2. Build and run the docker image in development

```
$ docker-compose -f docker-compose.development.yml up --build

```

#### 3. Load the data into the database

From the project directory `dockerflaskapi/` run the following command:

```
$ cat loansproject_data.dump | docker exec -i dockerflaskapi_postgres.flaskapi_1 psql -U flask flask_api

```

There is a postgreSQL database manager running in docker. Simply access
it in your browser at `localhost: 8000` using the access credentials 
above and

- Email: pgadmin4@pgadmin.org
- Password: pgadmin

Inside PgAdmin Dashboard go to 'Quick Links' > 'Add New Server'. Under 
'General' provide any Name, e.g. 'Loans Project Dev'.

Under 'Connection' provide 'Host: postgres', 'Username: flask', 
'Password: flaskdb', and 'Save'. You can now access the database tables.

#### 4. Run the web application

In directory `dockerflaskapi` run the following command:

```
$ docker-compose -f docker-compose.development.yml exec web.flaskapi sh -c 'pipenv run flask run --host=0.0.0.0 --port=5000'

```

The Swagger Api documentation can be accessed in your browser at `localhost:80`.


## Running the tests

TravisCI is preconfigured to run automated tests on:

- PRs related to merges into master or any branch named `ci-<name>`
- `git push` changes into master or any branch named `ci-<name>`

For manually running the tests:

### Run pytest

In directory `dockerflaskapi`:

```
$ docker-compose -f docker-compose.testing.yml up -d --build

$ docker-compose -f docker-compose.testing.yml exec web.testing sh -c 'pytest -v --disable-warnings'

$ docker-compose -f docker-compose.testing.yml down


```


## General Instructions

### Changing The Project Name

One of the first tasks when adjusting the business logic for repurposing this project is to
the change following files:

```
# In uwsgi.ini replace the following line:

# module = loansapi.api
module = <your project>.api


# In docker-compose.development.yml
environment:
  # - FLASK_APP=loansapi/api.py
  - FLASK_APP=<your project>/api.py

#In .travis.yml change the environment variables:
env:
  # - APP_DIR="$TRAVIS_BUILD_DIR/loansapp"
  - APP_DIR="$TRAVIS_BUILD_DIR/<your project>"

# Rename the parent directory
$ cp -r loansapp <your project>
$ rm -r loansapp

```

*NOTE*: It is recommended to use PyCharm for the refactoring the project directories, since all import statements need to
be changed along the way.

### Changing Nginx Configurations

The flask docker is based on a project from *Sebastián Ramírez* [uwsgi-nginx-flask-docker](https://github.com/tiangolo/uwsgi-nginx-flask-docker). 

A few adjustments have been made on the way, but all configuration and general instruction references are holding for 
this project, too.  


## Author

**OlafMarangone** - *Initial work* - [Gitlab](https://github.com/olmax99/dockerflaskapi.git)  
contact: olmax99@gmail.com

## License

MIT
 
Copyright (C) 2019 Olaf Marangone  

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to the following conditions:  
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.  
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE 
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS 
OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
