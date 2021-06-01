# Deploy to AWS Sagemaker

Deploy to Sagemaker

## Prerequisites

* An active AWS account configured on the machine with AWS CLI installed and configured
  * Install instruction: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html
  * Configure AWS account instruction: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html

* Docker is installed and running on the machine.
  * Install instruction: https://docs.docker.com/install

## Deployment steps

### 1. Create and push docker image to AWS ECR

  1. Create ECR

     To create a new ECR repository, run AWS command in the terminal

     ```bash
     $ aws ecr create-repository \
        --repository-name bentoml-example-repo
     ```

  2. Get ECR info

     A. Get ProxyEndpoint

        ```bash
        $ aws ecr get-authorization-token --registry-id REGISTRY_ID_FROM_CREATE_ECR_COMMAND
        ```

     B. Docker login ECR

      Get docker login info

        ```bash
        $ aws get-login --registry-id REGISTRY_ID_FROM_CREATE_ECR_COMMAND

        # Example output
        docker login -u AWS -p <password> -e none https://<aws_account_id>.dkr.ecr.<region>.amazonaws.com
        ```

      Run the output from the previous command

  3. Build docker image

     In the terminal

     ```
     $docker build
     ```

  4. Push to ECR

2. create sagemaker model
3. create sagemaker endpoint config
4. create sagemaker endpoint