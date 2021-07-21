import os


def generate_api_gateway_template(
    project_dir, api_gateway_name, api_name, endpoint_name
):
    cf_template = f"""
    AWSTemplateFormatVersion: '2010-09-09'

    Description: An API Gateway to invoke Sagemaker Endpoint

    Resources:

      ApiGatewayRestApi:
        Type: AWS::ApiGateway::RestApi
        Properties:
          ApiKeySourceType: HEADER
          Description: An API Gateway to invoke Sagemaker Endpoint
          EndpointConfiguration:
            Types:
              - EDGE
          Name: {api_gateway_name}

      ApiGatewayResource:
        Type: AWS::ApiGateway::Resource
        Properties:
          ParentId: !GetAtt ApiGatewayRestApi.RootResourceId
          PathPart: '{api_name}'
          RestApiId: !Ref ApiGatewayRestApi

      ApiGatewayMethod:
        Type: AWS::ApiGateway::Method
        Properties:
          ApiKeyRequired: false
          AuthorizationType: NONE
          HttpMethod: POST
          Integration:
            ConnectionType: INTERNET
            Credentials: !GetAtt ApiGatewayIamRole.Arn
            IntegrationHttpMethod: POST
            PassthroughBehavior: WHEN_NO_MATCH
            TimeoutInMillis: 29000
            Type: AWS
            Uri: !Sub 'arn:aws:apigateway:${{AWS::Region}}:runtime.sagemaker:path/endpoints/{endpoint_name}/invocations'
            IntegrationResponses:
              - SelectionPattern: 2\\d{{2}}
                StatusCode: 200
              - SelectionPattern: 4\\d{{2}}
                StatusCode: 400
              - SelectionPattern: 5\\d{{2}}
                StatusCode: 500
          MethodResponses:
            - StatusCode: 200
            - StatusCode: 400
            - StatusCode: 500
          OperationName: 'invokeSagemaker'
          ResourceId: !Ref ApiGatewayResource
          RestApiId: !Ref ApiGatewayRestApi

      ApiGatewayModel:
        Type: AWS::ApiGateway::Model
        Properties:
          ContentType: 'application/json'
          RestApiId: !Ref ApiGatewayRestApi
          Schema: {{}}

      ApiGatewayStage:
        Type: AWS::ApiGateway::Stage
        Properties:
          DeploymentId: !Ref ApiGatewayDeployment
          Description: Sagemaker prod API
          RestApiId: !Ref ApiGatewayRestApi
          StageName: 'prod'

      ApiGatewayDeployment:
        Type: AWS::ApiGateway::Deployment
        DependsOn: ApiGatewayMethod
        Properties:
          Description: Sagemaker Endpoint API Deployment
          RestApiId: !Ref ApiGatewayRestApi

      ApiGatewayIamRole:
        Type: AWS::IAM::Role
        Properties:
          AssumeRolePolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Sid: ''
                Effect: 'Allow'
                Principal:
                  Service:
                    - 'apigateway.amazonaws.com'
                Action:
                  - 'sts:AssumeRole'
          Path: '/'
          Policies:
            - PolicyName: SagemakerAccess
              PolicyDocument:
                Version: '2012-10-17'
                Statement:
                  - Effect: 'Allow'
                    Action: 'sagemaker:InvokeEndpoint'
                    Resource: 'arn:aws:sagemaker:*:213386773652:endpoint/*'
    """

    template_file_path = os.path.join(project_dir, "api_template.yaml")
    with open(template_file_path, "w") as f:
        f.write(cf_template)

    return template_file_path
