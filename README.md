# Python Athena Stack [![Build Status](https://travis-ci.org//olmax99/dockerflaskapi.png)](https://travis-ci.org//olmax99/dockerflaskapi)

This is a web API project with a capability of distributed background 
workers for reading and storing larger datasets to AWS S3. It is combined 
with a light-weight DWH system utilizing AWS Athena.

--- 

**Project Design**

![Graph](images/dockerflaskapi.png)

## Prerequisites

For local development, the following components are required on the local machine:

+ Pipenv
+ Python Version 3.6.9
+ Docker installed [official Docker docs](https://docs.docker.com/)
+ Docker-Compose
+ RexRay Docker Plugin s3fs [https://rexray.readthedocs.io/en/stable/](https://rexray.readthedocs.io/en/stable/)
+ aws-cli installed [https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)

---


**NOTE:** Currently, Celery will fail on Python 3.7 due to conflicting 
naming of packages using `async`, which is now a keyword in Python. 
Temporarily downgraded to `3.6.9` until solved.


## I. Quickstart Development

---

**NOTE:** For demonstration purposes, this project assumes the [https://github.com/olmax99/serverlessbaseapi](https://github.com/olmax99/serverlessbaseapi) 
project as the data source and to be up and running.

### 1. Preparing the project environment

In PyCharm:

In PyCharm > Settings > Project Interpreter:
+ Verify that the Project Interpreter `Pipenv(webflaskapi)` is selected.

*NOTE:*   PyCharm should be opened with the webflaskapi directory as the
  top folder. Otherwise the pipenv interpreter might behave in an 
  unexpected way.

In PyCharm > Tools > Python Integrated Tools > Testing

+ Set default test runner: pytest

*NOTE:*   Installing from PyCharm or even from both terminal and 
  PyCharm should make no difference. Ensure that *Pipfile.lock* is 
  up-to-date. In Pipfile directory simply run `$ pipenv lock` for 
  creating a new `Pipfile.lock`.


### 2. Prepare the environment files and external tools

#### a. Docker-compose environment files

There are two files required that are containing the database access credentials 
that need to be created manually.

From the terminal:

**NOTE:** All values provided here need to match the values provided in
the `.env` file.

Inside the `dockerflaskapi` directory:

```
$ vim .env.web.dev

# parameters need to match with those of .env file
REDIS_URI=redis://:super_secret2@redis.flaskapi:6379/0
CELERY_BROKER_URL=redis://:super_secret2@redis.flaskapi:6379/0
CELERY_RESULT_BACKEND=redis://:super_secret2@redis.flaskapi:6379/0

$ vim .env.worker.dev

CELERY_BROKER_URL=redis://:super_secret2@redis.flaskapi:6379/0
CELERY_RESULT_BACKEND=redis://:super_secret2@redis.flaskapi:6379/0
PERMITS_URL=<cfn-apigateway-public-url>                   <-- Get from 'serverless base api' project
PERMITS_KEY=<x-api-key>                                   <-- Get from 'serverless base api' project
AWS_ACCESS_KEY_ID=<aws access id>
AWS_SECRET_ACCESS_KEY=<aws secret key>

$ vim .env

REDIS_PASSWD=super_secret2
REDIS_URI=redis://:super_secret2@redis.flaskapi:6379/0

```

#### b. Aws credentials file

**NOTE:** The IAM access credentials need to be created manually. It is
recommended to further reduce the following access policies:

- AmazonS3FullAccess
- AmazonAthenaFullAccess
- AWSCloudFormationFullAccess 

```
$ aws configure --profile <dev name>

# AWS Access Key ID [None]: <dev access id>
# AWS Secret Access Key [None]: <dev access key>
# Default region name [None]: eu-central-1
# Default output format [None]: json

```

**NOTE:** The name of your custom profile needs to match the aws credentials 
in `.env.worker.dev`.

#### c. RexRay s3fs Docker Volume plugin

A s3fs compatible docker volume needs to be created.

```
# Will create an S3 bucket along with a docker rexray volume
$ docker volume create --driver rexray/s3fs:0.11.4 --name flaskapi-dev-rexray-data

# Verify that rexray docker plugin is set up correctly

$ docker plugin ls

# EXPECTED:
# 1e8d8739nm  rexray/s3fs:0.11.4   REX-Ray FUSE Driver for Amazon Simple Storag…   true

$ docker run -ti -v flaskapi-dev-rexray-data:/data nginx:latest mount | grep "/data"

# EXPECTED:
# s3fs on /data type fuse.s3fs (rw,nosuid,nodev,relatime,user_id=0,group_id=0)


```

### 3. Run the project

#### 1. Set the applications run mode

There are two ways of running the app in development mode.

1. If you want to run the Flask app directly from nginx/uwsgi, comment 
out the line starting with `command: ...` in `dockerflaskapi/docker-compose.development.yml`:

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

#### 3. Run the web application

**NOTE:** Skip this step if Flask is running directly from nginx/uwsgi

---

Only in DEBUG mode, in directory `dockerflaskapi` run the following command:

```
$ docker-compose -f docker-compose.development.yml exec web.flaskapi sh -c 'pipenv run flask run --host=0.0.0.0 --port=5000'

# OPTIONALLY - view real-time worker logs
$ docker logs -f dockerflaskapi_worker.flaskapi_1

```

**NOTE:** Changes to the code base of the worker will always need a full restart.

---

1. The Swagger Api documentation can be accessed in your browser at `localhost:5000`.
2. Flower can be accessed on `localhost:5555`

#### 4. Create a development table in AWS Athena

```bash
$ aws cloudformation validate-template --template-body file://cloudformation.development.athena.yml

$ aws cloudformation create-stack --stack-name flaskapi-dev-athena-01 \
  --template-body file://cloudformation.development.athena.yml

```

Using DBeaver (or any Athena compatible database manager for that matter), 
verify that the partition can be queried:

```sql
SELECT application_number, permit_record_id
FROM dev_flaskapi_01.dev_permits_01
WHERE partitiontime='2019-09-27';


```

**Delete resources:**

```
$ aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE
$ aws cloudformation delete-stack --stack-name dev-flaskapi-01

```


## II. Running the tests

TravisCI is preconfigured to run automated tests on:

- PRs related to merges into master or any branch named `ci-<name>`
- `git push` changes into master or any branch named `ci-<name>`

For manually running the tests:

### Run pytest

In directory `dockerflaskapi`:

```
$ docker-compose -f docker-compose.testing.yml up -d --build

$ docker-compose -f docker-compose.testing.yml exec web.testing sh -c 'pytest -v --disable-warnings'

$ docker-compose -f docker-compose.testing.yml exec worker.testing sh -c 'pytest -v --disable-warnings'

$ docker-compose -f docker-compose.testing.yml down


```

## III. Quickstart Production

Use [https://dbeaver.io/](https://dbeaver.io/) for directly connecting to the Athena Database.

Launch [https://github.com/olmax99/serverlessbaseapi](https://github.com/olmax99/serverlessbaseapi) for 
the Demo endpoint as external data source. 

### 1. Create Project Base Buckets

**NOTE:** Two persistent Buckets are needed for this project to run: 
  1. `flaskapi-cloudformation-eu-central-1` holds all templates and container instance logs
  2. `flaskapi-staging-datastore-eu-central-1` will be connected to the AWS Glue Table and 
  contains the final partitioned data. Latter will then be read in by Athena.

Even after you clean up a project, you want these buckets to persist. Therefore they are NOT
part of the CloudFormation templates. Create them manually.

### 2. Prepare Task Definition

**NOTE**: Currently, Ecs Secrets are NOT implemented. The target endpoint of the loading data
worker job is hard coded. Replace it with your current endpoint parameters.

In `cloudformation/staging/services/cloudformation.flaskapi.web.yml` change the following lines:
  - `PERMITS_URL`
  - `PERMITS_KEY`

```
ContainerDefinitions:
  - Name: worker-flaskapi
    Image: !Sub ${EcrRepoName}/celery-flaskapi
    # Soft limit, which can be escaped
    MemoryReservation: 256
    # TODO: Implement ECS secrets
    Environment:
        - Name: 'CELERY_BROKER_URL'
        Value: !Sub 'redis://:@${RedisHostName}:6379/0'
        - Name: 'CELERY_RESULT_BACKEND'
        Value: !Sub 'redis://:@${RedisHostName}:6379/0'
        - Name: 'C_FORCE_ROOT'
        Value: 'true'
        - Name: 'PERMITS_URL'
        Value: 'https://dk0uwspefe.execute-api.eu-central-1.amazonaws.com/dev/permits/all-permits-json'
        - Name: 'PERMITS_KEY'
        Value: 'ReASbdH1cI6H1K0pO3DqW4ZehZHwD0vE92uF3Flt'

```

### 3. Create Elastic Container Registry

#### a. Get an ECR access token and create ECR repositories

**NOTE:** There can be only one registry per AWS account

```sh
$ make ecr

```

#### b. Push images to ECR

**NOTE:** The local images should exist after having build the project for development.

**NOTE:** Currently, there is no automated CI pipeline. For this reason you need to rebuild
and push the images after every code change manually.

```sh
$ export ECR_REPO_PREFIX=<your ECR label>

# Tag Images with the ECR URL prefix
$ make tag

# Push Images
$ make push

```

### 4. Launch ECS Cluster

#### a. Create deployment bucket and upload files

See [Master template](https://github.com/olmax99/dockerflaskapi/blob/master/cloudformation.staging.ecs.master.yml) for 
detailed Bucket specification. Other than that create the Bucket manually.

From project directory
```sh
# OPTIONALLY
$ aws cloudformation validate-template --template-body file://cloudformation/staging/cloudformation.staging.ecs.master.yml

$ make templates

```

#### b. Launch master template

```sh
$ make cluster

```

#### c. Connect to FlaskApi

```sh
# Activate ovpn connection throught network settings
$ make vpn

```

In browser use: 
  - `http://<internal-flaskapi-staging-alb-endpoint>:5000/`
  - `http://<internal-flaskapi-staging-alb-endpoint>:5555/`

**NOTE:** Target location in `flaskapi--rexray-data-vol` needs to be fixed!! Parquet files need
to be located inside the `data folder` before they can be processed into the data store. This would
need to be configured in the rexray configuration inside the container instance `LaunchConfiguration`.

### FAQ ECS

1. How to get details on the cluster node ami in use?

  *`aws ssm get-parameters --names /aws/service/ecs/optimized-ami/amazon-linux-2/recommended --region ${AWS::Region}`

1. What triggers a scale-up or scale-down of the cluster nodes, respectively? How can it be tested?

  * The current autoscaling configuration simply attempts to reach the desired number of nodes. The 
  desired cluster size is defined in `cloudformation.staging.ecs.master` with property `ClusterMinNodes`.
  This means that in the current setup the cluster size is being kept at this size, and does not vary on
  load or any other events.

  Only an `Unhealthy` signal might lead to temporary changes in the cluster size. However, the autoscaling
  will always attempt to get to the desired state.

2. How does a scale-up or scale-down of task containers translates to an scale-up or scale-down of the cluster nodes?

  * Currently, there are no interchangeable effects between the ecs cluster nodes and the task containers,
  other than unhealthy nodes will be replaced by the autoscaling group.


## IV. General Instructions

### Changing The Project Name

One of the first tasks when adjusting the business logic for repurposing this project is to
the change following files:

```
# In uwsgi.ini replace the following line:

# module = flaskapi.api
module = <your project>.api


# In docker-compose.development.yml
environment:
  # - FLASK_APP=flaskapi/api.py
  - FLASK_APP=<your project>/api.py

#In .travis.yml change the environment variables:
env:
  # - APP_DIR="$TRAVIS_BUILD_DIR/webflaskapi"
  - APP_DIR="$TRAVIS_BUILD_DIR/<your project>"

# Rename the parent directory
$ cp -r webflaskapi <your project>
$ rm -r webflaskapi

```

*NOTE*: It is recommended to use PyCharm for the refactoring of the project
directories, since all import statements need to be changed along the way.

### Changing Nginx Configurations

The flask docker is based on a project from *Sebastián Ramírez* [uwsgi-nginx-flask-docker](https://github.com/tiangolo/uwsgi-nginx-flask-docker). 

A few adjustments have been made along the way, but all configuration and
general instruction references are holding for this project, too.

### Log in to Production Bastion Host

SSH forward into bastion host in order to further jump through private network instances. You need to 
use the private IP address!

```sh
# Activate the vpn connection in network settings
$ make vpn

$ ssh -A -i /path/to/<VPN Access Key>.pem ec2-user@<Private IP>

```

## Where to go from here?

- Secure data in AWS Athena [https://docs.aws.amazon.com/athena/latest/ug/security.html](https://docs.aws.amazon.com/athena/latest/ug/security.html)
- Use RexRay with ECS [https://aws.amazon.com/blogs/compute/amazon-ecs-and-docker-volume-drivers-amazon-ebs/](https://aws.amazon.com/blogs/compute/amazon-ecs-and-docker-volume-drivers-amazon-ebs/) `[DONE]`
- Integrate JWT with with Flask + schema verfication with endpoints [https://flask-jwt-extended.readthedocs.io/en/stable/](https://flask-jwt-extended.readthedocs.io/en/stable/)
- Implement ECS secrets [https://docs.aws.amazon.com/AmazonECS/latest/developerguide/specifying-sensitive-data-tutorial.html](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/specifying-sensitive-data-tutorial.html)
- Run a very large dataset through the infrastructure: [https://data.cityofnewyork.us/Transportation/2018-Yellow-Taxi-Trip-Data/t29m-gskq](https://data.cityofnewyork.us/Transportation/2018-Yellow-Taxi-Trip-Data/t29m-gskq)
- Implement an automated CI/CD with [CodeBuild](https://docs.aws.amazon.com/codebuild/latest/userguide/getting-started.html) and [CodePipeline](https://docs.aws.amazon.com/codepipeline/latest/userguide/tutorials-four-stage-pipeline.html)
- Integrate with BI Platforms such as [Chartio](https://chartio.com/docs/quick-start/), [Tableau](https://www.tableau.com/about/blog/2017/5/connect-your-s3-data-amazon-athena-connector-tableau-103-71105), [KNIME](https://www.knime.com/knime-software-on-amazon-web-services)
- Replace EC2 container instances with a logic to integrate Spot instances


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
