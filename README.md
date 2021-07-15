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


## Deploy Iris Classifier from BentoML quickstart guide to AWS Sagemaker

1. Build and save Bento Bundle from [BentoML quick start guide](https://github.com/bentoml/BentoML/blob/master/guides/quick-start/bentoml-quick-start-guide.ipynb)

2. Create Sagemaker deployment with the deployment tool

    Run deploy script in the command line:

    ```bash
    $ BENTO_BUNDLE_PATH=$(bentoml get IrisClassifier:latest --print-location -q)
    $ python deploy.py $BENTO_BUNDLE_PATH my-sagemaker-deployment sagemaker_config.json

    #Sample output
    Create ECR repo my-sagemaker-deployment-repo
    Build and push image 192023623294.dkr.ecr.us-west-2.amazonaws.com/my-sagemaker-deployment-repo:irisclassifier-20210630132202_b1fe9d
    Create Sagemaker model my-sagemaker-deployment-model
    Create Sagemaker endpoint confg my-sagemaker-deployment-config
    Create Sagemaker endpoint my-sagemaker-deployment-endpoint


    Get Sagemaker deployment information and status

    ```bash
    $ python describe.py my-sagemaker-deployment

    # Sample output
    [
      {
        "EndpointName": "my-sagemaker-deployment-endpoint",
        "EndpointArn": "arn:aws:sagemaker:us-west-2:192023623294:endpoint/my-sagemaker-deployment-endpoint",
        "EndpointConfigName": "my-sagemaker-deployment-config",
        "EndpointStatus": "Creating",
        "CreationTime": "2021-06-30T15:30:28.554000-07:00",
        "LastModifiedTime": "2021-06-30T15:30:28.554000-07:00"
      },
    ]
    ```

3. Make sample request against deployed service

    ```bash
    $ curl -i \
        --header "Content-Type: application/json" \
        --request POST \
        --data '[[5.1, 3.5, 1.4, 0.2]]' \
        https://btml-test-script.herokuapp.com/predict

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

### Create a new deployment

Use Command line

```bash
python deploy.py <BENTO_BUNDLE_PATH> <DEPLOYMENT_NAME> <CONFIG_JSON default is sagemaker_config.json>
```

For example:

```bash
$ MY_BUNDLE_PATH=$(bentoml get IrisClassifier:latest --print-location -q)
$ python deploy.py $MY_BUNDLE_PATH my_deployment sagemaker_config.json
```

Use Python API

```python
from deploy import deploy_to_sagemaker

deploy_to_sagemaker(BENTO_BUNDLE_PATH, DEPLOYMENT_NAME, CONFIG_JSON)
```


#### Available configuration options for Sagemaker deployment

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
