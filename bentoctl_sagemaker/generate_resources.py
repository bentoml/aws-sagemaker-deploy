from bentoml.saved_bundle import load_bento_service_metadata
from sagemaker.lambda_function import LAMBDA_FUNCION_CODE


def gen_model(model_name, image_tag, timeout, num_of_workers):
    """
    Generates the Sagemaker model that will be loaded to the endpoint instances.
    """

    model = {
        "SagemakerModel": {
            "Type": "AWS::SageMaker::Model",
            "Properties": {
                "ModelName": model_name,
                "ExecutionRoleArn": {"Fn::GetAtt": ["ExecutionRole", "Arn"]},
                "PrimaryContainer": {
                    "Image": image_tag,
                    "ImageConfig": {"RepositoryAccessMode": "Platform"},
                    "Environment": {
                        "BENTOML_GUNICORN_TIMEOUT": timeout,
                        "BENTOML_GUNICORN_NUM_OF_WORKERS": num_of_workers,
                    },
                },
            },
        },
        "ExecutionRole": {
            "Type": "AWS::IAM::Role",
            "Properties": {
                "ManagedPolicyArns": [
                    "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
                ],
                "AssumeRolePolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"Service": ["sagemaker.amazonaws.com"]},
                            "Action": ["sts:AssumeRole"],
                        }
                    ],
                },
            },
        },
    }

    return model


def gen_endpoint_config(
    endpoint_config_name,
    model_name,
    initial_instance_count,
    instance_type,
    data_capture_sample_percent,
    data_capture_s3_prefix,
    enable_data_capture=False,
):
    """
    Generates the endpoint_config for the Sagemaker Endpoint. We can specify all the
    production variants here.
    """
    endpoint_config = {
        "SagemakerEndpointConfig": {
            "Type": "AWS::SageMaker::EndpointConfig",
            "DependsOn": "SagemakerModel",
            "Properties": {
                # "EndpointConfigName": endpoint_config_name,
                "DataCaptureConfig": {
                    "EnableCapture": enable_data_capture,
                    "InitialSamplingPercentage": data_capture_sample_percent,
                    "DestinationS3Uri": data_capture_s3_prefix,
                    "CaptureOptions": [
                        {"CaptureMode": "Input"},
                        {"CaptureMode": "Output"},
                    ],
                },
                "ProductionVariants": [
                    {
                        "InitialInstanceCount": initial_instance_count,
                        "InitialVariantWeight": 1,
                        "InstanceType": instance_type,
                        "ModelName": {"Fn::GetAtt": ["SagemakerModel", "ModelName"]},
                        "VariantName": "default",
                    }
                ],
            },
        },
    }

    return endpoint_config


def gen_endpoint(endpoint_name, endpoint_config_name):
    """
    Generate the endpoint resource
    """
    endpoint = {
        "SagemakerEndpoint": {
            "Type": "AWS::SageMaker::Endpoint",
            "DependsOn": "SagemakerEndpointConfig",
            "Properties": {
                "EndpointConfigName": {
                    "Fn::GetAtt": ["SagemakerEndpointConfig", "EndpointConfigName"]
                },
                "EndpointName": endpoint_name,
                "RetainAllVariantProperties": False,
            },
        },
    }

    return endpoint


def gen_api_gateway(api_gateway_name, endpoint_name, timeout, bento_bundle_path):
    # basic API Gateway Config
    api_gateway = {
        "HttpApi": {
            "Type": "AWS::ApiGatewayV2::Api",
            "Properties": {
                "Name": api_gateway_name,
                "Description": "API Gateway proxy to lambda function that exposes sagemaker endpoint",
                "ProtocolType": "HTTP",
            },
        },
        "HttpApiIntegration": {
            "Type": "AWS::ApiGatewayV2::Integration",
            "DependsOn": ["Lambdafn"],
            "Properties": {
                "Description": "Lambda Integration",
                "IntegrationMethod": "POST",
                "IntegrationUri": {
                    "Fn::Sub": "arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${Lambdafn.Arn}/invocations"
                },
                "PayloadFormatVersion": "2.0",
                "ApiId": {"Ref": "HttpApi"},
                "IntegrationType": "AWS_PROXY",
            },
        },
        "DefaultStage": {
            "Type": "AWS::ApiGatewayV2::Stage",
            "Properties": {
                "StageName": "$default",
                "AutoDeploy": True,
                "ApiId": {"Ref": "HttpApi"},
            },
        },
        "LambdaExecutionRole": {
            "Type": "AWS::IAM::Role",
            "Properties": {
                "ManagedPolicyArns": [
                    "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess",
                    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
                ],
                "AssumeRolePolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"Service": ["lambda.amazonaws.com"]},
                            "Action": ["sts:AssumeRole"],
                        }
                    ],
                },
            },
        },
        "Lambdafn": {
            "Type": "AWS::Lambda::Function",
            "Properties": {
                "Runtime": "python3.9",
                "Description": "Parse request and invoke Sagmeker Endpoint",
                "Timeout": timeout,
                "Role": {"Fn::Sub": "${LambdaExecutionRole.Arn}"},
                "Handler": "index.lambda_handler",
                "Code": {
                    "ZipFile": LAMBDA_FUNCION_CODE.format(endpoint_name=endpoint_name)
                },
                "TracingConfig": {"Mode": "Active"},
            },
        },
        "ApigatewayPermission": {
            "Type": "AWS::Lambda::Permission",
            "Properties": {
                "FunctionName": {"Fn::GetAtt": ["Lambdafn", "Arn"]},
                "Action": "lambda:InvokeFunction",
                "Principal": "apigateway.amazonaws.com",
                "SourceArn": {
                    "Fn::Sub": "arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${HttpApi}/*/*/*"
                },
            },
        },
    }

    # add routes from bentoservice to API Gateway
    bento_metadata = load_bento_service_metadata(bento_bundle_path)
    for api in bento_metadata.apis:
        route_name = f"{api.name}Route".lower()
        api_gateway[route_name] = {
            "Type": "AWS::ApiGatewayV2::Route",
            "DependsOn": ["HttpApiIntegration", "Lambdafn"],
            "Properties": {
                "ApiId": {"Ref": "HttpApi"},
                "RouteKey": f"POST /{api.route}",
                "Target": {
                    "Fn::Join": ["/", ["integrations", {"Ref": "HttpApiIntegration"}]]
                },
            },
        }

    return api_gateway
