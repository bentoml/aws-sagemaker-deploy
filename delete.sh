#!/usr/bin/env bash

if ! command -v aws &> /dev/null
then
    echo "aws could not be found"
    exit
fi

if [ "$#" -eq 1 ]; then
  DEPLOYMENT_NAME=$1
else
  echo "Must provide sagemaker deployment name"
  exit 1
fi

MODEL_REPO=$DEPLOYMENT_NAME-repo
MODEL_NAME=$DEPLOYMENT_NAME-model
ENDPOINT_CONFIG_NAME=$DEPLOYMENT_NAME-endpoint-config
ENDPOINT_NAME=$DEPLOYMENT_NAME-endpoint

aws sagemaker delete-endpoint --endpoint-name $ENDPOINT_NAME | python -c "import json, sys; print(json.load(sys.stdin))"
aws sagemaker delete-endpoint-config --endpoint-config-name $ENDPOINT_CONFIG_NAME | python -c "import json, sys; print(json.load(sys.stdin))"
aws sagemaker delete-model --model-name $MODEL_NAME | python -c "import json, sys; print(json.load(sys.stdin))"

# Use this command to delete the ECR repository
#aws ecr delete-repository --repository-name $MODEL_REPO --force