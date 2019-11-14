define message1
 Environment variable BASE_IP is required. Not set.
	Use following command:
        "$$ my_ip=`curl ipinfo.io | jq .ip`;eval my_ip=$${my_ip[i]};my_ip="$$myip/32"; export BASE_IP=$$my_ip"

endef

define message2
 Environment variable AWS_DOCKER_REPO is required. Not set.
	Use following command:
        "$$ my_aws_registry=`aws ecr describe-repositories | jq .repositories[0].repositoryUri`; \
        eval my_aws_registry=$${my_aws_registry[i]};my_aws_registry=`echo $$my_aws_registry | cut -d'/' -f1`; \
        export AWS_DOCKER_REPO=$$my_aws_registry"
     
endef



ifndef BASE_IP
export message1
$(error $(message1))
endif

ifndef AWS_DOCKER_REPO
$(error $(message2))
endif

define random_string
$(shell cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 13 | head -n 1)
endef


CURRENT_LOCAL_IP = $(BASE_IP)
ECR_REPO_PREFIX = $(AWS_DOCKER_REPO)


CFN_TEMPLATES_BUCKET := flaskapi-cloudformation-eu-central-1
VPN_CERTS_BUCKET := flaskapi-staging-openvpn-certs-eu-central-1
AWS_REGION := eu-central-1
PROJECT_NAME := flaskapi-staging
VPN_KEY_NAME := flaskapi-staging-bastion
NEW_UUID := $(call random_string, nan)

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

cluster: templates
	aws cloudformation --region ${AWS_REGION} create-stack --stack-name ${PROJECT_NAME} \
	--template-body file://cloudformation/staging/cloudformation.staging.ecs.master.yml \
	--parameters ParameterKey="EcrRepoPrefix",ParameterValue="${ECR_REPO_PREFIX}" \
	ParameterKey="VpnAccessKey",ParameterValue="${VPN_KEY_NAME}" \
	ParameterKey="LocalBaseIp",ParameterValue="${CURRENT_LOCAL_IP}" \
	ParameterKey="CloudformationBucket",ParameterValue="${CFN_TEMPLATES_BUCKET}" \
	ParameterKey="RexrayBucket",ParameterValue="${PROJECT_NAME}-rexray-data-lake-${NEW_UUID}" \
	--capabilities CAPABILITY_NAMED_IAM

vpn:
	aws s3 cp s3://${VPN_CERTS_BUCKET}/client/FlaskApiVPNClient.zip ~/Downloads/FlaskApiVPNClient/
	unzip ~/Downloads/FlaskApiVPNClient/FlaskApiVPNClient.zip -d ~/Downloads/FlaskApiVPNClient
	nmcli con import type openvpn file ~/Downloads/FlaskApiVPNClient/flaskapi_vpn_clientuser.ovpn

clean:
	aws cloudformation delete-stack --stack-name ${PROJECT_NAME}
	rm -r ~/Downloads/FlaskApiVPNClient
	nmcli con delete flaskapi_vpn_clientuser

