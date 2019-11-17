define random_string
$(shell cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 13 | head -n 1)
endef

CFN_TEMPLATES_BUCKET := flaskapi-staging-cfn-master-eu-central-1
VPN_CERTS_BUCKET := flaskapi-staging-openvpn-certs-eu-central-1
AWS_REGION := eu-central-1
PROJECT_NAME := flaskapi-staging
VPN_KEY_NAME := flaskapi-staging-bastion
NEW_UUID := $(call random_string)

define message1
 Environment variable BASE_IP is required. Not set.
	Use following command:
        "$$ my_ip=`curl ipinfo.io | jq .ip`;eval my_ip=$${my_ip[i]};my_ip="$$my_ip/32"; export BASE_IP=$$my_ip"

endef

define message2
 Environment variable AWS_DOCKER_REPO is required. Not set.
	Use following command:
        "$$ my_aws_registry=`aws ecr describe-repositories | jq .repositories[0].repositoryUri`; \
        eval my_aws_registry=$${my_aws_registry[i]};my_aws_registry=`echo $$my_aws_registry | cut -d'/' -f1`; \
        export AWS_DOCKER_REPO=$$my_aws_registry"
     
endef

define message3
 Create an S3 bucket, which is used as a datalake and shared mount in ECS.
 Environment variable REXRAY_VOLUME is required. Not set.
	Use following command:
        "export REXRAY_VOLUME=${PROJECT_NAME}-rexray-datalake-${NEW_UUID} && \
        aws s3 mb s3://${PROJECT_NAME}-rexray-datalake-${NEW_UUID}"

 [WARNING]: Wait ~10-15min until the bucket is fully provisioned in AWS. Otherwise
            docker mounts might fail.
endef

ifndef BASE_IP
export message1
$(error $(message1))
endif

ifndef AWS_DOCKER_REPO
$(error $(message2))
endif

ifndef REXRAY_VOLUME
$(error $(message3))
endif

define welcome

# -------------------------* **!!\\_WELCOME_/!!** *--------------------------- #
           ___
        .-9 9 `\\         Project:    ${PROJECT_NAME}
       =(:(::)= \;          Version:    NaN
         ||||    \\
         ||||      `-.
         \\|\\|         `,
        /               \\
       ;                  `'---.,
       |                        `\\
       ;                    /     |
       \                    |     /
        )           \  __,.--\   /
     .-' \,..._\     \`   .-'  .-'
     `-=``      `:    |\/-\/-\/`
                  `.__/
endef


CURRENT_LOCAL_IP = $(BASE_IP)
ECR_REPO_PREFIX = $(AWS_DOCKER_REPO)

export welcome
help:
	@echo "$$welcome"
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

ecr:
	$(aws ecr get-login --no-include-email --region ${AWS_REGION})
	aws ecr create-repository --repository-name nginx-flaskapi
	aws ecr create-repository --repository-name celery-flaskapi
	aws ecr create-repository --repository-name flower-flaskapi

tag:
	docker tag celery-flaskapi ${ECR_REPO_PREFIX}/celery-flaskapi
	docker tag nginx-flaskapi ${ECR_REPO_PREFIX}/nginx-flaskapi
	docker tag mher/flower ${ECR_REPO_PREFIX}/flower-flaskapi

push:
	docker push ${ECR_REPO_PREFIX}/celery-flaskapi
	docker push ${ECR_REPO_PREFIX}/nginx-flaskapi
	docker push ${ECR_REPO_PREFIX}/flower-flaskapi

templates:
	aws s3 cp --recursive cloudformation/staging/cluster s3://${CFN_TEMPLATES_BUCKET}/staging/
	aws s3 cp --recursive cloudformation/staging/services s3://${CFN_TEMPLATES_BUCKET}/staging/

# ParameterKey="RexrayBucket",ParameterValue="${PROJECT_NAME}-rexray-data-lake-${NEW_UUID}" \
cluster:		## Launch the project in CloudFormation.
cluster: templates	## '$NEW_UUID': lowercase alphanumeric only (constraints: docker vol + bucket naming)
	aws cloudformation --region ${AWS_REGION} create-stack --stack-name ${PROJECT_NAME} \
	--template-body file://cloudformation/staging/cloudformation.staging.ecs.master.yml \
	--parameters ParameterKey="EcrRepoPrefix",ParameterValue="${ECR_REPO_PREFIX}" \
	ParameterKey="VpnAccessKey",ParameterValue="${VPN_KEY_NAME}" \
	ParameterKey="LocalBaseIp",ParameterValue="${CURRENT_LOCAL_IP}" \
	ParameterKey="CloudformationBucket",ParameterValue="${CFN_TEMPLATES_BUCKET}" \
	ParameterKey="RexrayBucket",ParameterValue="${REXRAY_VOLUME}" \
	--capabilities CAPABILITY_NAMED_IAM

vpn:			## Connect to OpenApi(<LoadBalancerDNS>:5000) and Flower(<LoadBalancerDNS>:5555).
	aws s3 cp s3://${VPN_CERTS_BUCKET}/client/FlaskApiVPNClient.zip ~/Downloads/FlaskApiVPNClient/
	unzip ~/Downloads/FlaskApiVPNClient/FlaskApiVPNClient.zip -d ~/Downloads/FlaskApiVPNClient
	nmcli con import type openvpn file ~/Downloads/FlaskApiVPNClient/flaskapi_vpn_clientuser.ovpn

clean:			## Remove the project and save money.
	aws cloudformation delete-stack --stack-name ${PROJECT_NAME}
	rm -r ~/Downloads/FlaskApiVPNClient
	nmcli con delete flaskapi_vpn_clientuser

