# BentoML Sagemaker deployment tool

## Prerequisites

- An active AWS account configured on the machine with AWS CLI installed and configured
    - Install instruction: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html
    - Configure AWS account instruction: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html
- Docker is installed and running on the machine.
    - Install instruction: https://docs.docker.com/install
  
- Install required python packages
    - `$ pip install -r requirements.txt`
    


## Deploy Sagemaker endpoint

Run deploy script to create a Sagemaker deployment

```bash
$ python deploy.py <DEPLOYMENT_NAME> <BENTO_BUNDLE_PATH> <API_NAME> <CONFIG_JSON default is sagemaker_config.json>
```

For example:
```bash
$ MY_BUNDLE_PATH=$(bentoml get IrisClassifier:latest --print-location -q)
$ python deploy.py my_deployment $MY_BUNDLE_PATH predict
# To specific a different configuration file
$ python deploy.py my_deployment $MY_BUNDLE_PATH predict path/to/another_config.json
```

### Available configuration options for Sagemaker deployment

Customize these options in the `sagemaker_config.json` or 

`timeout`: (Int) Timeout for API request in seconds

`workers`: (Int) Number of works for Bento API server

`region`: (Str) AWS region where Sagemaker endpoint is deployed to

`instance_type`: (Str) The ML compute instance type for Sagemaker endpoint. See https://docs.aws.amazon.com/cli/latest/reference/sagemaker/create-endpoint-config.html for available instance types

`initial_instance_count`: (Int) Number of instances to launch initially.

`enable_data_capture`: (Bool) Enable Sagemaker capture data from requests and responses and store the captured data to AWS S3

`data_capture_s3_prefix`: (Str) S3 bucket path for store captured data

`data_capture_sample_percent`: (Int) Percentage of the data will be captured to S3 bucket.


## Update Sagemaker endpoint

```bash
$ python update.py <DEPLOYMENT_NAME> <BENTO_BUNDLE_PATH> <API_NAME> <CONFIG_JSON default is sagemaker_config.json>
```


## Describe Sagemaker endpoint

```bash
$ python get.py <DEPLOYMENT_NAME>
```

## Delete Sagemaker endpoint

```bash
$ python delete.py <DEPLOYMENT_NAME>
```
