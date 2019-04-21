[ https://hub.docker.com/r/tiangolo/uwsgi-nginx-flask/#project-generators ]
[ https://github.com/tiangolo/uwsgi-nginx-docker ]

USEFUL COMMANDS

$ docker-compose up -d --build
$ docker-compose exec web sh -c 'pipenv run flask run --host=0.0.0.0 --port=5000'


TODOS:
x Fill "launch project"
x Fill "run in production"
x Try running docker as development and production "hello world - flask"
x Modify docker to have simple api project (sqlite)
x configure pipenv in docker
x Modify docker to have simple api project (including mysql-docker)
x Determine if docker needs nested structure along the way as in "Working with submodules" (e.g. for tests !!!)
x [ OPTIONALLY ] implement project structure [ see: "Quick Start for bigger projects structured as a Python package" ]
x seperate project from docker folder and put it in a common namespace ( create simlink to code )
x sort out structure (create common function for database an flask instanciation)
x repair DELETE API call (Error "Object is already attached to session")    <-- related to connexion
x save skel project ( for python apis )
x Build full API project [ https://realpython.com/flask-connexion-rest-api/ ]  DO NOT USE CONNEXION !!!
        

x Remove Warning:
  UserWarning: Neither SQLALCHEMY_DATABASE_URI nor SQLALCHEMY_BINDS is set. Defaulting SQLALCHEMY_DATABASE_URI to "sqlite:///:memory:".
  [ https://stackoverflow.com/questions/43466927/sqlalchemy-database-uri-not-set ]
  >> DONE

x Remove Warning
  ChangedInMarshmallow3Warning: strict=False is not recommended. In marshmallow 3.0, schemas will always be strict. See https://marshmallow.readthedocs.io/en/latest/upgrading.html#schemas-are-always-strict
  ChangedInMarshmallow3Warning
  >> just temporary warning
- Create single project
- Replace tiangalo
- implement testing
- allow postgreSQL


( After pytest OR while using pytest ) 
- !!! Learn Starlette !!! [ https://github.com/tiangolo/uvicorn-gunicorn-starlette-docker ]
- allow for asynchronous calls

-------------------------------------------------------------------------------------------------------------------------

Python REST APIs With Flask and Connexion

-------------------------------------------------------------------------------------------------------------------------

- create an templates folder and make it accessible via /home   <-- "/" is already occupied by index.html from statics

$ pipenv install connexion[swaggerui]

- Replace flask app creation:

    # Create the application instance
    app = connexion.App(__name__, specification_dir='openapi/')     <-- create folder for openapi.yml file

    # Read the swagger.yml file to configure the endpoints
    app.add_api('my_api.yml')
    
- view full openapi specification:
    [ https://github.com/OAI/OpenAPI-Specification/blob/OpenAPI.next/versions/3.0.0.md ]    <-- also version 2.0

 
* How to do the requests?

    1. CREATE NEW USER
        $ curl -X POST -H "Content-Type: application/json" -d '{"username": "Petra","email": "petramus@gmail.com"}' http://localhost:80/api/user
    2. SHOW ALL USERS
        $ curl http://localhost:80/api/user
    3. GET USER DETAIL
        $ curl http://localhost:80/api/user/2
    4. UPDATE USER
        $ curl -X PUT -H "Content-Type: application/json" -d '{"username": "Berta","email": "bertamus@gmail.com"}' http://localhost:80/api/user/2
    5. DELETE USER
        $ curl -X DELETE http://localhost:80/api/user/2





-------------------------------------------------------------------------------------------------------------------------

LAUNCH PROJECT

-------------------------------------------------------------------------------------------------------------------------

Project Structure

flaskApiMySql
├── flaskapp
│   ├── app
│   │   ├── api
│   │   │   ├── api.py
│   │   │   ├── endpoints
│   │   │   └── __init__.py
│   │   ├── core
│   │   │   ├── app_setup.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── models
│   │       ├── __init__.py
│   │       └── user.py
│   ├── Dockerfile
│   ├── Pipfile
│   ├── Pipfile.lock
│   └── uwsgi.ini
└── dockerflaskapi
    ├── app -> ../app
    ├── docker-compose.override.yml
    └── docker-compose.yml

    
CREATE INITIAL DB

$ docker exec -ti dockerflaskapi_web_1 /bin/bash
$ pipenv install
$ pipenv shell
$ python

>>> from app.main import db, ma
>>> from app.models import user
>>> db.create_all()
>>> db.session.commit()

    
    
TESTING

$ docker run -d --name flaskapi -p 80:80 flaskapi
$ curl -I 'http://localhost:80'
    
    HTTP/1.1 200 OK
    Server: nginx/1.15.8
    Date: Fri, 18 Jan 2019 16:54:15 GMT
    Content-Type: text/html; charset=utf-8
    Content-Length: 105
    Connection: keep-alive
    
[ OPTIONALLY ] Change port in Dockerfile:
    FROM tiangolo/uwsgi-nginx-flask:python3.7
    ENV LISTEN_PORT 8080
    EXPOSE 8080
    COPY ./app /app
    
[ OPTIONALLY ] Customize uwsgi.ini file location looking for <application> instead of app:
    ENV UWSGI_INI /application/uwsgi.ini
    COPY ./application /application
    WORKDIR /application
    
[ OPTIONALLY ] Define Nginx configurations using ENV values in Dockerfile:
    - Nginx process numbers (workers)
    - maximum connections per worker
    - maximum open files
    
    COPY ./< name >.conf /etc/nginx/conf.d/< name >.conf 
    

DEBUGGING | DEV MODE

STEP 1: Docker dry run
# Will keep container alive even if flask crashes due to code changes 
    $ docker run -d --name FlaskApi -p 80:80 -v $(pwd)/app:/app -e FLASK_APP=main.py -e FLASK_DEBUG=1 flaskapi bash -c "while true ; do sleep 10 ; done"

STEP 2: Launch flask manually
    $ docker exec -it FlaskApi /bin/bash
    $ pipenv run flask run --host=0.0.0.0 --port=80

STEP 3: Monitor flask server and see errors if it breaks

DOCKER COMPOSE:

    $ docker-compose up -d --build
    $ docker-compose exec web sh -c 'pipenv run flask run --host=0.0.0.0 --port=80'


RUN IN PRODUCTION

    $ docker run -d --name FlaskApi -p 80:80 flaskapi

OR USING VOLUME MAPPING
In repostory directory:
    $ docker run -d --name FlaskApi -p 80:80 -v $(pwd)/app:/app flaskapi 

NOTE: !!! Volume mapping not recommended in production !!!




