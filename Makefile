CFN_TEMPLATES_BUCKET := flaskapi-cloudformation-eu-central-1
AWS_REGION := eu-central-1

ecr:
	$(aws ecr get-login --no-include-email --region ${AWS_REGION})
	aws ecr create-repository --repository-name nginx-flaskapi
	aws ecr create-repository --repository-name celery-flaskapi
	aws ecr create-repository --repository-name redis

tag:
	docker tag celery-flaskapi ${ECR_REPO_PREFIX}/celery-flaskapi
	docker tag nginx-flaskapi ${ECR_REPO_PREFIX}/nginx-flaskapi
	docker tag redis:5.0-apline ${ECR_REPO_PREFIX}/redis:5.0-alpine

push:
	docker push ${ECR_REPO_PREFIX}/celery-flaskapi
	docker push ${ECR_REPO_PREFIX}/nginx-flaskapi
	docker push ${ECR_REPO_PREFIX}/redis:5.0-alpine

templates:
	aws s3 cp --recursive cloudformation/staging/cluster s3://${CFN_TEMPLATES_BUCKET}/staging/
	aws s3 cp --recursive cloudformation/staging/services s3://${CFN_TEMPLATES_BUCKET}/staging/

cluster:
	aws cloudformation --region ${AWS_REGION} update-stack --stack-name flaskapi-staging \
	--template-body file://cloudformation/staging/cloudformation.staging.ecs.master.yml \
	--parameters ParameterKey="EcrRepoPrefix",ParameterValue="${ECR_REPO_PREFIX}" \
	--capabilities CAPABILITY_NAMED_IAM

