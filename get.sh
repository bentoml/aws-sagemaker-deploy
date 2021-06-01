#!/usr/bin/env bash

if ! command -v aws &> /dev/null
then
    echo "aws could not be found"
    exit
fi

if [ "$#" -eq 1 ]; then
  DEPLOYMENT_NAME=$1
else
  echo "Must provide deployment name"
  exit 1
fi

ENDPOINT_NAME=$DEPLOYMENT_NAME-endpoint

aws sagemaker describe-endpoint --endpoint-name $DEPLOYMENT_NAME | python -c "import json, sys; print(json.load(sys.stdin))"
