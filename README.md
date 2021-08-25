# BentoML Sagemaker deployment tool

[![Generic badge](https://img.shields.io/badge/Release-Alpha-<COLOR>.svg)](https://shields.io/)

AWS Sagemaker is a fully managed service for building ML models. BentoML provides great support
for deploying BentoService to AWS Sagemaker without the additional process and work from users. With BentoML, users can enjoy the performance of Sagemaker with any popular ML frameworks.

## Prerequisites

- An active AWS account configured on the machine with AWS CLI installed and configured
    - Install instruction: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html
    - Configure AWS account instruction: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html
- Docker is installed and running on the machine.
    - Install instruction: https://docs.docker.com/install

- Install required python packages
    - `$ pip install -r requirements.txt`


## Quickstart

You can try out the deployment script with the IrisClassifier for the iris dataset that is given in the [BentoML quick start guide](https://github.com/bentoml/BentoML/blob/master/guides/quick-start/bentoml-quick-start-guide.ipynb)

1. Build and save Bento Bundle from [BentoML quick start guide](https://github.com/bentoml/BentoML/blob/master/guides/quick-start/bentoml-quick-start-guide.ipynb)

2. Create Sagemaker deployment with the deployment tool. Make sure you have the configuration file setup for your deployment. You can copy over the [sample config file](sagemaker_config.json) to get started. The config definitions are provided [here](#configuration-options)

    Run deploy script in the command line:

    ```bash
    $ BENTO_BUNDLE_PATH=$(bentoml get IrisClassifier:latest --print-location -q)
    $ python deploy.py $BENTO_BUNDLE_PATH my-sagemaker-deployment --config_json sagemaker_config.json

    #Sample output
    Create ECR repo my-sagemaker-deployment-repo
    Build and push image 1234.dkr.ecr.ap-south-1.amazonaws.com/my-sagemaker-deployment-repo:irisclassifier-20210726160058_ca2fac
    Deploying stack my-sagemaker-deployment
    Done!
    ```

    Get Sagemaker deployment information and status

    ```
    $ python describe.py my-sagemaker-deployment

    # Sample output
    {
      "Stacks": [
        {
          "StackId": "arn:aws:cloudformation:ap-south-1:1234:stack/my-sagemaker-deployment-endpoint/08b61cb0-ee02-11eb-a637-020384318d50",
          "StackName": "my-sagemaker-deployment-endpoint",
          "ChangeSetId": "arn:aws:cloudformation:ap-south-1:1234:changeSet/awscli-cloudformation-package-deploy-1627297805/608bd7e3-6321-4e3a-9e2c-81a9c8ac0
                "Description": "An API Gateway to invoke Sagemaker Endpoint",
          "CreationTime": "2021-07-26T11:10:06.918000+00:00",
          "LastUpdatedTime": "2021-07-26T11:10:12.310000+00:00",
          "RollbackConfiguration": {},
          "StackStatus": "CREATE_COMPLETE",
          "DisableRollback": false,
          "NotificationARNs": [],
          "Capabilities": [
            "CAPABILITY_IAM"
                ],
          "Outputs": [
            {
              "OutputKey": "OutputApiId",
              "OutputValue": "yr3v9vh407",
              "Description": "Api generated Id",
              "ExportName": "OutputApiId"
            },
            {
              "OutputKey": "EndpointURL",
              "OutputValue": "yr3v9vh407.execute-api.ap-south-1.amazonaws.com/prod"
            }
           ],
          "Tags": [],
          "EnableTerminationProtection": false,
          "DriftInformation": {
            "StackDriftStatus": "NOT_CHECKED"
          }
        }
      ]
    }
    ```

3. Make sample request against deployed service

    ```bash
    $ curl -i \
        --header "Content-Type: application/json" \
        --request POST \
        --data '[[5.1, 3.5, 1.4, 0.2]]' \
        yr3v9vh407.execute-api.ap-south-1.amazonaws.com/prod/predict

    # Sample Output
    HTTP/1.1 200 OK
    Connection: keep-alive
    Content-Type: application/json
    X-Request-Id: f499b6d0-ad9b-4d79-850a-3dc058bd67b2
    Content-Length: 3
    Date: Mon, 28 Jun 2021 02:50:35 GMT
    Server: Python/3.7 aiohttp/3.7.4.post0
    Via: 1.1 vegur

    [0]%
    ```

4. Delete Sagemaker deployment

    ```bash
    python delete.py my-sagemaker-deployment
    ```

## Deployment operations

### configuration options

A sample configuration file has been given has been provided [here](sagemaker_config.json). Feel free to copy it over and change it for you specific deployment values

* `api_name`: User-defined API function for the inference
* `timeout`: timeout for API request in seconds
* `workers`: Number of workers for Bento API server
* `region`: AWS region where Sagemaker endpoint is deploying to
* `iam_role`: (optional) if provided with an AWS Role name, that role will be
used for creating the Sagemaker endpoint. Make sure this Role has
AmazonSagemakerFullAccess and ECR - BatchGetImage permissions. If this option is
not provided a role with the sagemaker permissions will be selected for you
(based on the roles in your aws-cli profile).
* `instance_type`: The ML compute instance type for Sagemaker endpoint. See https://docs.aws.amazon.com/cli/latest/reference/sagemaker/create-endpoint-config.html for available instance types
* `initial_instance_count`: Number of instances to launch initially.
* `enable_data_capture`: Enable Sagemaker capture data from requests and responses and store the captured data to AWS S3
* `data_capture_s3_prefix`: S3 bucket path for store captured data
* `data_capture_sample_percent`: Percentage of the data will be captured to S3 bucket.

### Create a new deployment

Use Command line

```bash
python deploy.py <BENTO_BUNDLE_PATH> <DEPLOYMENT_NAME> --config_json <CONFIG_JSON default is sagemaker_config.json>
```

For example:

```bash
$ MY_BUNDLE_PATH=$(bentoml get IrisClassifier:latest --print-location -q)
$ python deploy.py $MY_BUNDLE_PATH my_deployment --config_json sagemaker_config.json
```

Use Python API

```python
from deploy import deploy_to_sagemaker

deploy_to_sagemaker(BENTO_BUNDLE_PATH, DEPLOYMENT_NAME, CONFIG_JSON)
```

To create and push a model image to ECR without deploying the stack, use the flag `--skip_stack_deployment`

### Update an existing deployment

Use Command Line
```bash
python update.py <DEPLOYMENT_NAME> <BENTO_BUNDLE_PATH> <API_NAME> <CONFIG_JSON default is sagemaker_config.json>
```


Use Python API

```python
from update import update_deployment

update_deployment(BENTO_BUNDLE_PATH, DEPLOYMENT_NAME, CONFIG_JSON)
```

### Describe deployment status and information

Use Command line

```bash
python get.py <DEPLOYMENT_NAME>
```


Use Python API

```python
from describe import describe_deployment
describe_deployment(DEPLOYMENT_NAME)
```

### Delete deployment

Use Command line

```bash
python delete.py <DEPLOYMENT_NAME>
```

Use Python API

```python
from delete import delete_deployment

delete_deployment(DEPLOYMENT_NAME)
```
