# Deploy to AWS Sagemaker

Deploy to Sagemaker

### Prerequisites

* An active AWS account configured on the machine with AWS CLI installed and configured
  * Install instruction: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html
  * Configure AWS account instruction: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html

* Docker is installed and running on the machine.
  * Install instruction: https://docs.docker.com/install

### Deployment steps:

1. Create docker image
  1. buid docker image
  2. create ecr
  3. push to ecr
2. create sagemaker model
3. create sagemaker endpoint config
4. create sagemaker endpoint