def gen_model(model_name, image_tag, api_name, timeout, num_of_workers):
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
                        "API_NAME": api_name,
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


def gen_api_gateway(api_gateway_name, api_name, endpoint_name):
    api_gateway = {
        "ApiGatewayRestApi": {
            "Type": "AWS::ApiGateway::RestApi",
            "Properties": {
                "ApiKeySourceType": "HEADER",
                "BinaryMediaTypes": ["multipart~1form-data"],
                "Description": "An API Gateway to invoke Sagemaker Endpoint",
                "EndpointConfiguration": {"Types": ["EDGE"]},
                "Name": api_gateway_name,
            },
        },
        "ApiGatewayResource": {
            "Type": "AWS::ApiGateway::Resource",
            "Properties": {
                "ParentId": {"Fn::GetAtt": ["ApiGatewayRestApi", "RootResourceId"]},
                "PathPart": api_name,
                "RestApiId": {"Ref": "ApiGatewayRestApi"},
            },
        },
        "ApiGatewayMethod": {
            "Type": "AWS::ApiGateway::Method",
            "Properties": {
                "ApiKeyRequired": False,
                "AuthorizationType": "NONE",
                "HttpMethod": "POST",
                "RequestParameters": {
                    "method.request.header.Accept": "false",
                    "method.request.header.Content-Type": "false",
                },
                "Integration": {
                    "ConnectionType": "INTERNET",
                    "Credentials": {"Fn::GetAtt": ["ApiGatewayIamRole", "Arn"]},
                    "IntegrationHttpMethod": "POST",
                    "PassthroughBehavior": "WHEN_NO_MATCH",
                    "RequestParameters": {
                        "integration.request.header.Accept": "method.request.header.Accept",
                        "integration.request.header.Content-Type": "method.request.header.Content-Type",
                    },
                    "TimeoutInMillis": 29000,
                    "Type": "AWS",
                    "Uri": {
                        "Fn::Sub": f"arn:aws:apigateway:${{AWS::Region}}:runtime.sagemaker:path/endpoints/{endpoint_name}/invocations"
                    },
                    "IntegrationResponses": [
                        {"SelectionPattern": "2\\d{2}", "StatusCode": 200},
                        {"SelectionPattern": "4\\d{2}", "StatusCode": 400},
                        {"SelectionPattern": "5\\d{2}", "StatusCode": 500},
                    ],
                },
                "MethodResponses": [
                    {"StatusCode": 200},
                    {"StatusCode": 400},
                    {"StatusCode": 500},
                ],
                "OperationName": "invokeSagemaker",
                "ResourceId": {"Ref": "ApiGatewayResource"},
                "RestApiId": {"Ref": "ApiGatewayRestApi"},
            },
        },
        "ApiGatewayModel": {
            "Type": "AWS::ApiGateway::Model",
            "Properties": {
                "ContentType": "application/json",
                "RestApiId": {"Ref": "ApiGatewayRestApi"},
                "Schema": {},
            },
        },
        "ApiGatewayStage": {
            "Type": "AWS::ApiGateway::Stage",
            "Properties": {
                "DeploymentId": {"Ref": "ApiGatewayDeployment"},
                "Description": "Sagemaker prod API",
                "RestApiId": {"Ref": "ApiGatewayRestApi"},
                "StageName": "prod",
            },
        },
        "ApiGatewayDeployment": {
            "Type": "AWS::ApiGateway::Deployment",
            "DependsOn": "ApiGatewayMethod",
            "Properties": {
                "Description": "Sagemaker API deployment",
                "RestApiId": {"Ref": "ApiGatewayRestApi"},
            },
        },
        "ApiGatewayIamRole": {
            "Type": "AWS::IAM::Role",
            "Properties": {
                "AssumeRolePolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "",
                            "Effect": "Allow",
                            "Principal": {"Service": ["apigateway.amazonaws.com"]},
                            "Action": ["sts:AssumeRole"],
                        }
                    ],
                },
                "Path": "/",
                "Policies": [
                    {
                        "PolicyName": "SagemakerAccess",
                        "PolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": "sagemaker:InvokeEndpoint",
                                    "Resource": {
                                        "Fn::Sub": "arn:aws:sagemaker:*:${AWS::AccountId}:endpoint/*"
                                    },
                                }
                            ],
                        },
                    }
                ],
            },
        },
    }

    return api_gateway
