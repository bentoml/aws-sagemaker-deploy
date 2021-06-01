#!/usr/bin/env bash


if ! command -v aws &> /dev/null
then
    echo "aws command could not be found"
    exit
fi

if [ "$#" -eq 3 ]; then
  BENTO_BUNDLE_PATH=$1
  DEPLOYMENT_NAME=$2
  API_NAME=$3
else
  echo "Must provide deployment name, bundle path and API name"
  exit 1
fi

exit 0

MODEL_REPO_NAME=$DEPLOYMENT_NAME-repo
MODEL_NAME=$DEPLOYMENT_NAME-model
ENDPOINT_CONFIG_NAME=$DEPLOYMENT_NAME-endpoint-config
ENDPOINT_NAME=$DEPLOYMENT_NAME-endpoint

# Create ECR repository
REGISTRY_ID=$(aws ecr create-repository --repository-name $MODEL_REPO_NAME | python -c "import json, sys; result=json.load(sys.stdin); print(result['repository']['registryId'])")

# login docker
aws get-login --registry-id --registry-id $REGISTRY_ID

# Generate Sagemaker deployable
DEPLOYABLE_PATH=$(python ./bentoml_sagemaker/generate_deployable $BENTO_BUNDLE_PATH)

# Build docker image and push to ECR
IMAGE_PATH=abc
docker build
docker push

# Get ARN
ARN=$(aws sts get-caller-identity | python -c "import json, sys; result=json.load(sys.stdin); print(result['Arn'])")

# Create Sagemaker model
MODEL_INFO=$(python ./bentoml_sagemaker/generate_model_info $IMAGE_PATH $API_NAME)

# Create Sagemaker endpoint config
aws sagemaker create-model --model-name $MODEL_NAME --primary-container $MODEL_INFO --execution-role-arn $ARN

# Create Sagemaker endpoint
aws sagemaker
echo $ENDPOINT_NAME