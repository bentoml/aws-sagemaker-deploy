<div align="center">
    <h1>AWS Sagemaker Operator</h1>
</div>

Sagemaker is a fully managed service for building ML models. BentoML provides great support
for deploying BentoService to AWS Sagemaker without the additional process and work from users. With [BentoML serving framework](https://github.com/bentoml/BentoML) and [bentoctl](https://github.com/bentoml/bentoctl) users can enjoy the performance and scalability of Sagemaker with any popular ML frameworks.

> **Note:** This operator is compatible with BentoML version 1.0.0 and above. For older versions, please switch to the branch `pre-v1.0` and follow the instructions in the README.md.


## Table of Contents

   * [Quickstart with bentoctl](#quickstart-with-bentoctl)
   * [Configuration options](#configuration-options)
   * [Troubleshooting](#troubleshooting)


## Quickstart with bentoctl

This quickstart will walk you through deploying a bento as an AWS Sagemaker Endpoint. Make sure to go through the [prerequisites](#prerequisites) section and follow the instructions to set everything up.

### Prerequisites

1. BentoML version 1.0 or above. Please follow the [Installation guide](https://docs.bentoml.org/en/latest/installation.html).
2. Terraform - [Terraform](https://www.terraform.io/) is a tool for building, configuring, and managing infrastructure. Installation instruction: www.terraform.io/downloads
3. AWS CLI - installed and configured with an AWS account with permission to Sagemaker, Lambda and ECR. Please follow the [Installation guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
4. Docker - Install instruction: [docs.docker.com/install](https://docs.docker.com/install)
5. A built Bento project. For this guide, we will use the Iris classifier bento from the [BentoML quickstart guide](https://docs.bentoml.org/en/latest/quickstart.html#quickstart). You can also use your own Bentos that are available locally.

### Steps

1. Install bentoctl via pip
    ```
    $ pip install bentoctl
    ```

2. Install AWS Sagemaker operator

    Bentoctl will install the official AWS Sagemaker operator and its dependencies.

    ```
    $ bentoctl operator install aws-sagemaker
    ```

3. Initialize deployment with bentoctl

    Follow the interactive guide to initialize the deployment project.

    ```bash
    $ bentoctl init
    
    Bentoctl Interactive Deployment Config Builder

    Welcome! You are now in interactive mode.

    This mode will help you setup the deployment_config.yaml file required for
    deployment. Fill out the appropriate values for the fields.

    (deployment config will be saved to: ./deployment_config.yaml)

    api_version: v1
    name: quickstart
    operator: aws-sagemaker
    template: terraform
    spec:
        region: ap-south-1
        instance_type: ml.t2.medium
        initial_instance_count: 1
        timeout: 60
        enable_data_capture: False
        destination_s3_uri:
        initial_sampling_percentage: 1
    filename for deployment_config [deployment_config.yaml]:
    deployment config generated to: deployment_config.yaml
    ✨ generated template files.
      - ./main.tf
      - ./bentoctl.tfvars
    ```
    This will also run the `bentoctl generate` command for you and will generate the `main.tf` terraform file, which specifies the resources to be created and the `bentoctl.tfvars` file which contains the values for the variables used in the `main.tf` file.

4. Build and push AWS sagemaker compatible docker image to the registry

    Bentoctl will build and push the sagemaker compatible docker image to the AWS ECR repository.

    ```bash
    bentoctl build -b iris_classifier:latest -f deployment_config.yaml

    Step 1/22 : FROM bentoml/bento-server:1.0.0a6-python3.8-debian-runtime
     ---> 046bc2e28220
    Step 2/22 : ARG UID=1034
     ---> Using cache
     ---> f44cfa910c52
    Step 3/22 : ARG GID=1034
     ---> Using cache
     ---> e4d5aed007af
    Step 4/22 : RUN groupadd -g $GID -o bentoml && useradd -m -u $UID -g $GID -o -r bentoml
     ---> Using cache
     ---> fa8ddcfa15cf
    ...
    Step 22/22 : CMD ["bentoml", "serve", ".", "--production"]
     ---> Running in 28eccee2f650
     ---> 98bc66e49cd9
    Successfully built 98bc66e49cd9
    Successfully tagged quickstart:kiouq7wmi2gmockr
    🔨 Image build!
    Created the repository quickstart
    The push refers to repository
    [213386773652.dkr.ecr.ap-south-1.amazonaws.com/quickstart]
    kiouq7wmi2gmockr: digest:
    sha256:e1a468e6b9ceeed65b52d0ee2eac9e3cd1a57074eb94db9c263be60e4db98881 size: 3250
    63984d77b4da: Pushed
    2bc5eef20c91: Pushed
    ...
    da0af9cdde98: Layer already exists
    e5baccb54724: Layer already exists
    🚀 Image pushed!
    ✨ generated template files.
      - ./bentoctl.tfvars
      - ./startup_script.sh
    ```
    The iris-classifier service is now built and pushed into the container registry and the required terraform files have been created. Now we can use terraform to perform the deployment.
    
5. Apply Deployment with Terraform

   1. Initialize terraform project. This installs the AWS provider and sets up the terraform folders.
      ```bash
      $ terraform init
      ```

   2. Apply terraform project to create Sagemaker deployment

        ```bash
        $ terraform apply -var-file=bentoctl.tfvars -auto-approve

        aws_iam_role.iam_role_lambda: Creating...
        aws_iam_role.iam_role_sagemaker: Creating...
        aws_apigatewayv2_api.lambda: Creating...
        aws_apigatewayv2_api.lambda: Creation complete after 1s [id=rwfej5qsf6]
        aws_cloudwatch_log_group.api_gw: Creating...
        aws_cloudwatch_log_group.api_gw: Creation complete after 1s [id=/aws/api_gw/quickstart-gw]
        aws_apigatewayv2_stage.lambda: Creating...
        aws_apigatewayv2_stage.lambda: Creation complete after 3s [id=$default]
        aws_iam_role.iam_role_sagemaker: Creation complete after 7s [id=quickstart-sagemaker-iam-role]
        aws_sagemaker_model.sagemaker_model: Creating...
        aws_iam_role.iam_role_lambda: Creation complete after 8s [id=quickstart-lambda-iam-role]
        aws_lambda_function.fn: Creating...
        ...


        Apply complete! Resources: 1 added, 0 changed, 0 destroyed.

        Outputs:

        endpoint = "https://rwfej5qsf6.execute-api.ap-south-1.amazonaws.com/"
        ecr_image_tag = "213386773652.dkr.ecr.ap-south-1.amazonaws.com/quickstart:sfx3dagmpogmockr"
        ```

6. Test deployed endpoint

    The `iris_classifier` uses the `/classify` endpoint for receiving requests so the full URL for the classifier will be in the form `{EndpointUrl}/classify`.

    ```bash
    URL=$(terraform output -json | jq -r .endpoint.value)classify
    curl -i \
      --header "Content-Type: application/json" \
      --request POST \
      --data '[5.1, 3.5, 1.4, 0.2]' \
      $URL

    HTTP/2 200
    date: Thu, 14 Apr 2022 23:02:45 GMT
    content-type: application/json
    content-length: 1
    apigw-requestid: Ql8zbicdSK4EM5g=

    0%
    ```

> Note: You can also [invoke the Sagemaker endpoint directly](https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_runtime_InvokeEndpoint.html). If there is only one service, SageMaker deployment will choose that one. If there is more than one, you can specify which service to use by passing the `X-Amzn-SageMaker-Custom-Attributes` header with the name of the service as value.
   
7. Delete deployment
    Use the `bentoctl destroy` command to remove the registry and the deployment

    ```bash
    bentoctl destroy -f deployment_config.yaml

## Configuration Options

A sample configuration file has been given has been provided [here](sagemaker_config.json). Feel free to copy it over and change it for you specific deployment values

* `region`: AWS region where Sagemaker endpoint is deploying to
* `instance_type`: The ML compute instance type for Sagemaker endpoint. See https://docs.aws.amazon.com/cli/latest/reference/sagemaker/create-endpoint-config.html for available instance types
* `initial_instance_count`: Number of instances to launch initially.
* `timeout`: timeout for API request in seconds
* `enable_data_capture`: Enable Sagemaker capture data from requests and responses and store the captured data to AWS S3
* `destination_s3_uri`: S3 bucket path for store captured data
* `initial_sampling_percentage`: Percentage of the data will be captured to S3 bucket.

## Troubleshooting
By default sagemaker is configured with cloudwatch for metrics and logs. To see the cloudwatch logs for the deployment

1. Open the Amazon Cloudwatch console at https://console.aws.amazon.com/cloudwatch/.
2. In the navigation pane, choose Logs -> Log groups.
3. Head over to /aws/sagemaker/Endpoints/<deployment_name>-endpoint
4. Choose the latest logs streams
