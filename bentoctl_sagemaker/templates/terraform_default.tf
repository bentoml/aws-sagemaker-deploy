terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.2.0"
    }
  }
}

provider "aws" {
  region = var.region
}

################################################################################
# Input variable definitions
################################################################################

variable "deployment_name" {
  type = string
}

variable "image_tag" {
  type = string
}

variable "image_repository" {
  type = string
}

variable "image_version" {
  type = string
}

variable "region" {
  type = string
}

variable "timeout" {
  type = number
}

variable "instance_type" {
  type = string
}
variable "initial_instance_count" {
  type = number
}

################################################################################
# Resource definitions
################################################################################

data "aws_ecr_repository" "service" {
  name = var.image_repository
}

data "aws_ecr_image" "service_image" {
  repository_name = data.aws_ecr_repository.service.name
  image_tag       = var.image_version
}

resource "aws_iam_role" "iam_role_sagemaker" {
  name                = "${var.deployment_name}-sagemaker-iam-role"
  managed_policy_arns = ["arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"]
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_sagemaker_model" "sagemaker_model" {
  name               = "${var.deployment_name}-model"
  execution_role_arn = resource.aws_iam_role.iam_role_sagemaker.arn
  primary_container {
    image = "${data.aws_ecr_repository.service.repository_url}@${data.aws_ecr_image.service_image.id}"
    mode  = "SingleModel"
  }
}

resource "aws_sagemaker_endpoint_configuration" "endpoint_config" {
  name = "${var.deployment_name}-endpoint-config"

  production_variants {
    initial_instance_count = var.initial_instance_count
    initial_variant_weight = 1.0
    instance_type          = var.instance_type
    model_name             = aws_sagemaker_model.sagemaker_model.name
    variant_name           = "default"
  }
}

resource "aws_sagemaker_endpoint" "sagemaker_endpoint" {
  name                 = "${var.deployment_name}-endpoint"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.endpoint_config.name
}

# Lambda function as a proxy to invoke Sagemaker Endpoint
resource "aws_iam_role" "iam_role_lambda" {
  name = "${var.deployment_name}-lambda-iam-role"
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ]
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

data "archive_file" "lambda_inline_zip" {
  type        = "zip"
  output_path = "/tmp/lambda_zip_inline.zip"
  source {
    content  = <<EOF
import boto3
from base64 import b64decode

def safeget(dct, *keys, default=None):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return default
    return dct

def lambda_handler(event, context):
    runtime = boto3.client('runtime.sagemaker')

    try:
        sagemaker_response = runtime.invoke_endpoint(
            EndpointName="${var.deployment_name}-endpoint",
            ContentType=safeget(event, 'headers', 'content-type', default='application/json'),
            CustomAttributes=safeget(event, 'path', default='')[1:],
            Body=b64decode(event.get('body')) if event.get('isBase64Encoded') else event.get('body')
        )
    except Exception as e:
        print(e)
        return {
            'statusCode': e.response.get('OriginalStatusCode'),
            'body': e.response.get('Error')['Message']
        }
    else:
        return {
            'statusCode': safeget(sagemaker_response, 'ResponseMetadata', 'HTTPStatusCode'),
            'body': sagemaker_response.get('Body').read()
        }
EOF
    filename = "index.py"
  }
}

resource "aws_lambda_function" "fn" {
  function_name = "${var.deployment_name}-function"
  description   = "A proxy service to invoke sagemaker endpoint."
  role          = aws_iam_role.iam_role_lambda.arn

  timeout          = 60
  runtime          = "python3.9"
  handler          = "index.lambda_handler"
  filename         = data.archive_file.lambda_inline_zip.output_path
  source_code_hash = data.archive_file.lambda_inline_zip.output_base64sha256

}

resource "aws_cloudwatch_log_group" "lg" {
  name = "/aws/lambda/${aws_lambda_function.fn.function_name}"

  retention_in_days = 30
}

# API Gateway for our service
resource "aws_apigatewayv2_api" "lambda" {
  name          = "${var.deployment_name}-gw"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "lambda" {
  api_id = aws_apigatewayv2_api.lambda.id

  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gw.arn

    format = jsonencode({
      requestId               = "$context.requestId"
      sourceIp                = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      protocol                = "$context.protocol"
      httpMethod              = "$context.httpMethod"
      resourcePath            = "$context.resourcePath"
      routeKey                = "$context.routeKey"
      status                  = "$context.status"
      responseLength          = "$context.responseLength"
      integrationErrorMessage = "$context.integrationErrorMessage"
      }
    )
  }
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id = aws_apigatewayv2_api.lambda.id

  integration_uri    = aws_lambda_function.fn.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "endpoints" {
  api_id = aws_apigatewayv2_api.lambda.id

  route_key = "POST /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}


resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fn.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.lambda.execution_arn}/*/*"
}
resource "aws_cloudwatch_log_group" "api_gw" {
  name = "/aws/api_gw/${aws_apigatewayv2_api.lambda.name}"

  retention_in_days = 30
}

################################################################################
# Output definitions
################################################################################
output "ecr_image_tag" {
  description = "Image Tag of the ECR image that was build and pushed"

  value = var.image_tag
}

output "base_url" {
  description = "Base URL for API Gateway stage."

  value = aws_apigatewayv2_stage.lambda.invoke_url
}
