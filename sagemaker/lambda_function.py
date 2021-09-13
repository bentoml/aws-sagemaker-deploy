LAMBDA_FUNCION_CODE = """
import json
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
            EndpointName="{endpoint_name}",
            ContentType=safeget(event, 'headers', 'content-type', default='application/json'),
            CustomAttributes=safeget(event, 'rawPath', default='')[1:],
            Body=b64decode(event.get('body')) if event.get('isBase64Encoded') else event.get('body')
        )
    except Exception as e:
        return {{
            'statusCode': e.response.get('OriginalStatusCode'),
            'body': e.response.get('Error')['Message']
        }}
    else:
        return {{
            'statusCode': safeget(sagemaker_response, 'ResponseMetadata', 'HTTPStatusCode'),
            'body': sagemaker_response.get('Body').read()
        }}
"""
