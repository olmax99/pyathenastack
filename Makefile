# create CURRENT_LOCAL_IP:
# $ foo=`curl ipinfo.io | jq .ip`;eval foo=${foo[i]};foo="$foo/32"; export CURRENT_LOCAL_IP=$foo
# create ECR_REPO_PREFIX:
# $ baz=`aws ecr describe-repositories | jq .repositories[0].repositoryUri`;eval baz=${baz[i]};baz=`echo $baz | cut -d'/' -f1`; export ECR_REPO_PREFIX=$baz

CFN_TEMPLATES_BUCKET := flaskapi-cloudformation-eu-central-1
VPN_CERTS_BUCKET := flaskapi-staging-openvpn-certs-eu-central-1
AWS_REGION := eu-central-1
PROJECT_NAME := flaskapi-staging
VPN_KEY_NAME := flaskapi-staging-bastion

ecr:
	$(aws ecr get-login --no-include-email --region ${AWS_REGION})
	aws ecr create-repository --repository-name nginx-flaskapi
	aws ecr create-repository --repository-name celery-flaskapi
	aws ecr create-repository --repository-name flower-flaskapi
	aws ecr create-repository --repository-name redis

tag:
	docker tag celery-flaskapi ${ECR_REPO_PREFIX}/celery-flaskapi
	docker tag nginx-flaskapi ${ECR_REPO_PREFIX}/nginx-flaskapi
	docker tag mher/flower ${ECR_REPO_PREFIX}/flower-flaskapi
	docker tag redis:5.0-apline ${ECR_REPO_PREFIX}/redis:5.0-alpine

push:
	docker push ${ECR_REPO_PREFIX}/celery-flaskapi
	docker push ${ECR_REPO_PREFIX}/nginx-flaskapi
	docker push ${ECR_REPO_PREFIX}/redis:5.0-alpine
	docker push ${ECR_REPO_PREFIX}/flower-flaskapi

templates:
	aws s3 cp --recursive cloudformation/staging/cluster s3://${CFN_TEMPLATES_BUCKET}/staging/
	aws s3 cp --recursive cloudformation/staging/services s3://${CFN_TEMPLATES_BUCKET}/staging/

cluster:
	aws cloudformation --region ${AWS_REGION} create-stack --stack-name ${PROJECT_NAME} \
	--template-body file://cloudformation/staging/cloudformation.staging.ecs.master.yml \
	--parameters ParameterKey="EcrRepoPrefix",ParameterValue="${ECR_REPO_PREFIX}" \
	ParameterKey="VpnAccessKey",ParameterValue="${VPN_KEY_NAME}" \
	ParameterKey="LocalBaseIp",ParameterValue="${CURRENT_LOCAL_IP}" \
	--capabilities CAPABILITY_NAMED_IAM

vpn:
	aws s3 cp s3://${VPN_CERTS_BUCKET}/client/FlaskApiVPNClient.zip ~/Downloads/FlaskApiVPNClient/
	unzip ~/Downloads/FlaskApiVPNClient/FlaskApiVPNClient.zip -d ~/Downloads/FlaskApiVPNClient
	nmcli con import type openvpn file ~/Downloads/FlaskApiVPNClient/flaskapi_vpn_clientuser.ovpn

clean:
	aws cloudformation delete-stack --stack-name ${PROJECT_NAME}
	rm -r ~/Downloads/FlaskApiVPNClient
	nmcli con delete flaskapi_vpn_clientuser

