<div align="center">
    <h1>AWS Sagemaker Operator</h1>
    <img src="https://img.shields.io/badge/Release-Alpha-<COLOR>.svg"/>
    <br>
    <p align="center">
      <img width=40% src="https://user-images.githubusercontent.com/5261489/149308825-912c7cec-a943-40f4-ac6c-ae21512bcbc5.png" alt="sagemaker logo"/>
    </p>
</div>

Sagemaker is a fully managed service for building ML models. BentoML provides great support
for deploying BentoService to AWS Sagemaker without the additional process and work from users. With BentoML, users can enjoy the performance of Sagemaker with any popular ML frameworks.

<!--ts-->

## Table of Contents

   * [Prerequisites](README.md#prerequisites)
   * [Quickstart](README.md#quickstart)
   * [The Internals](README.md#the-internals)
   * [Deployment operations](README.md#deployment-operations)
      * [configuration options](README.md#configuration-options)
      * [Create a new deployment](README.md#create-a-new-deployment)
      * [Update an existing deployment](README.md#update-an-existing-deployment)
      * [Describe deployment status and information](README.md#describe-deployment-status-and-information)
      * [Delete deployment](README.md#delete-deployment)

<!-- Added by: jjmachan, at: Thursday 13 January 2022 03:16:57 PM IST -->

<!--te-->
## Prerequisites

- An active AWS account configured on the machine with AWS CLI installed and configured
    - Install instruction: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html
    - Configure AWS account instruction: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html
- Docker is installed and running on the machine.
    - Install instruction: https://docs.docker.com/install

## Quickstart with bentoctl

Bentoctl is a CLI tool that you can use to deploy bentos to any cloud service. It makes configuring and managing your deployments super easy. To try this out make sure you have a working bentoml service. If not you can go through this quickstart with any of the examples from the [quickstart](https://github.com/bentoml/gallery/tree/main/quickstart).

With that lets deploy our first bento to sagemaker.

1. Install bentoctl via pip.
```
$ pip install bentoctl
```

2. Add AWS Sagemaker operator. Operators are plugins for bentoctl that add support for different cloud services.
```
$ bentoctl operator add aws-sagemaker
```

3. Deploy to sagemaker. When you call `bentoctl deploy` without passing a deployment_config.yaml it will launch interactive program to generate `deployment_config.yaml` file for your deployment. A `deployment_config.yaml` file configures your deployment. 
```
$ bentoctl deploy --display-deployment-info

Bentoctl Interactive Deployment Spec Builder

Welcome! You are now in interactive mode.

This mode will help you setup the deployment_spec.yaml file required for
deployment. Fill out the appropriate values for the fields.

(deployment spec will be saved to: ./deployment_spec.yaml)

api_version: v1
metadata:
    name: test
    operator: aws-sagemaker
spec:
    bento: testservice:bwmjyyttcoy6zdhpusy4drbc6
    region: ap-south-1
    skip_stack_deployment: False
    instance_type: ml.t2.medium
    initial_instance_count: 1
    workers: 3
    timeout: 60
    enable_data_capture: False
    data_capture_s3_prefix: ''
    data_capture_sample_size: 1
filename for deployment_config [deployment_config.yaml]:
deployment config generated to: deployment_config.yaml

deploying with deployment_spec.yaml...
Success!

{
│   'StackId': 'arn:aws:cloudformation:ap-south-1:213386773652:stack/test-stack/6e766f80-6992-11ec-b5ac-06ea5db619ac',
│   'StackName': 'test-stack',
│   'StackStatus': 'UPDATE_COMPLETE',
│   'CreationTime': '12/30/2021, 17:03:38',
│   'LastUpdatedTime': '01/04/2022, 16:37:14',
│   'EndpointUrl': 'https://fwxcofm8q7.execute-api.ap-south-1.amazonaws.com/Prod'
}
```

4. Check endpoint. We will try and test the endpoint The url for the endpoint given in the output of the describe command or you can also check the API Gateway through the AWS console.

    ```bash
    $ curl -i \
      --header "Content-Type: application/json" \
      --request POST \
      --data '[[5.1, 3.5, 1.4, 0.2]]' \
      https://fwxcofm8q7.execute-api.ap-south-1.amazonaws.com/Prod/predict

    # Sample output
    HTTP/1.1 200 OK
    Content-Type: application/json
    Content-Length: 3
    Connection: keep-alive
    Date: Tue, 21 Jan 2020 22:43:17 GMT
    x-amzn-RequestId: f49d29ed-c09c-4870-b362-4cf493556cf4
    x-amz-apigw-id: GrC0AEHYPHcF3aA=
    X-Amzn-Trace-Id: Root=1-5e277e7f-e9c0e4c0796bc6f4c36af98c;Sampled=0
    X-Cache: Miss from cloudfront
    Via: 1.1 bb248e7fabd9781d3ed921f068507334.cloudfront.net (CloudFront)
    X-Amz-Cf-Pop: SFO5-C1
    X-Amz-Cf-Id: HZzIJUcEUL8aBI0KcmG35rsG-71KSOcLUNmuYR4wdRb6MZupv9IOpA==

    [0]%

5. Delete deployment
```
$ bentoctl delete -f deployment_config.yaml
```

## Quickstart with scripts

You can try out the deployment script with the IrisClassifier for the iris dataset that is given in the [BentoML quick start guide](https://github.com/bentoml/gallery/tree/main/quickstart)

1. Build and save Bento Bundle from [BentoML quick start guide (https://github.com/bentoml/gallery/tree/main/quickstart)

2. Copy and change the [sample config file](sagemaker_config.json) given and change it according to your deployment specifications. Check out the [config section](#configuration-options) to find the differenet options.

3. Create Sagemaker deployment with the deployment tool. 
   
   Run deploy script in the command line:

    ```bash
    $ BENTO_BUNDLE_PATH=$(bentoml get IrisClassifier:latest --print-location -q)
    $ python deploy.py $BENTO_BUNDLE_PATH my-sagemaker-deployment sagemaker_config.json
    ```

    Get Sagemaker deployment information and status

    ```
    $ python describe.py my-sagemaker-deployment

    # Sample output
    {
    │   'StackId': 'arn:aws:cloudformation:ap-south-1:213386773652:stack/iristest-endpoint/edd9d500-095c-11ec-bc08-06418f3882f0',
    │   'StackName': 'iristest-endpoint',
    │   'StackStatus': 'CREATE_COMPLETE',
    │   'CreationTime': '08/30/2021, 06:38:47',
    │   'LastUpdatedTime': '08/30/2021, 06:38:52',
    │   'OutputApiId': '2f5qtdd2rf',
    │   'EndpointURL': 'https://2f5qtdd2rf.execute-api.ap-south-1.amazonaws.com/prod',
    │   'api_name': 'predict'
    }
    ```

4. Make sample request against deployed service. The url for the endpoint given in the output of the describe command or you can also check the API Gateway through the AWS console.

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

5. Delete Sagemaker deployment

    ```bash
    python delete.py my-sagemaker-deployment
    ```
## The Internals

This section is all about how the deployment tool works internally and how the actual deployment happens so that if needed you can modify this tool
to suit your deployment needs. Under the hood the deployment tool modifies the Bento Image to make it compatible with the [Sagemaker Endpoint](https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-inference-code.html). 
This image is then built and pushed into an ECR repository. All the other components are created as part of the cloudformation stack, which creates
the API Gateway, Lambda Function, Sagmaker Model, Sagemaker Endpoint Config and Sagemaker Endpoint. We have used an HTTP API Gateway + Lambda Function design to
expose the Sagemaker Endpoint since the Lambda function gives us a lot more flexibility.

<p align="center">
  <img src="https://user-images.githubusercontent.com/5261489/133879514-5b91eb1d-d7ae-4f03-965d-98107bd19962.png" alt="invocation arch"/>
</p>

For each bento endpoint that you have, the tool creates the corresponding route in HTTP Gateway which invokes the Lambda function which in turn invokes the Sagmaker endpoint and proxies the results back to the client. Since we are using Cloudformation to create the stack you can easily change/modify the resource to match your deployment needs. [`generate_resources.py`](sagemaker/generate_resources.py) contains the functions used to generate the cloudformation template which you can modifiy to suit you needs.

## Deployment operations

### configuration options

A sample configuration file has been given has been provided [here](sagemaker_config.json). Feel free to copy it over and change it for you specific deployment values

* `timeout`: timeout for API request in seconds
* `workers`: Number of workers for Bento API server
* `region`: AWS region where Sagemaker endpoint is deploying to
* `skip_stack_deployment`: If this flag is present in the config_file,
  deployment tool will only build and push the image to ECR and skip creation of
  sagemaker endpoint resources. With this you get your bentoml model build so
  that it runs and sagemaker and pushed to ECR and you can use other methods to
  create the resources to deploy the image.
* `instance_type`: The ML compute instance type for Sagemaker endpoint. See https://docs.aws.amazon.com/cli/latest/reference/sagemaker/create-endpoint-config.html for available instance types
* `initial_instance_count`: Number of instances to launch initially.
* `enable_data_capture`: Enable Sagemaker capture data from requests and responses and store the captured data to AWS S3
* `data_capture_s3_prefix`: S3 bucket path for store captured data
* `data_capture_sample_percent`: Percentage of the data will be captured to S3 bucket.

### Create a new deployment

Use Command line

```bash
python deploy.py <BENTO_BUNDLE_PATH> <DEPLOYMENT_NAME> <CONFIG_JSON default is ./sagemaker_config.json>
```

For example:

```bash
$ MY_BUNDLE_PATH=$(bentoml get IrisClassifier:latest --print-location -q)
$ python deploy.py $MY_BUNDLE_PATH my_deployment --config_json sagemaker_config.json
```

Use Python API

```python
from deploy import deploy

deploy(BENTO_BUNDLE_PATH, DEPLOYMENT_NAME, CONFIG_JSON)
```

To create and push a model image to ECR without deploying the stack, use the flag `--skip_stack_deployment`

### Update an existing deployment

Use Command Line
```bash
python update.py <DEPLOYMENT_NAME> <BENTO_BUNDLE_PATH> <API_NAME> <CONFIG_JSON default is sagemaker_config.json>
```


Use Python API

```python
from update import update

update(BENTO_BUNDLE_PATH, DEPLOYMENT_NAME, CONFIG_JSON)
```

### Describe deployment status and information

Use Command line

```bash
python get.py <DEPLOYMENT_NAME>
```


Use Python API

```python
from describe import describe
describe(DEPLOYMENT_NAME)
```

### Delete deployment

Use Command line

```bash
python delete.py <DEPLOYMENT_NAME>
```

Use Python API

```python
from delete import delete

delete(DEPLOYMENT_NAME)
```
