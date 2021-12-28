OPERATOR_NAME = 'aws-sagemaker'

OPERATOR_MODULE = 'bentoctl_sagemaker'

operator_schemas = {
    'region': {
        'required': True,
        'type': 'string',
        'help_message': 'AWS region'
    },
    'skip_stack_deployment': {
        'required': False,
        'type': 'boolean',
        'default': False,
        'help_message': 'Skip stack deployment on AWS'
    },
    'instance_type': {
        'required': True,
        'default': 'ml.t2.medium',
        'type': 'string',
        'help_message': 'Instance type for the sagemaker deployment'
    },
    'initial_instance_count': {
        'default': 1,
        'type': 'integer',
        'coerce': int,
        'required': True,
        'help_message': 'Initial instance count for the sagemaker deployment'
    },
    'workers': {
        'required': True,
        'default': 3,
        'coerce': int,
        'type': 'integer',
        'help_message': 'Number of workers for the sagemaker deployment'
    },
    'timeout': {
        'required': False,
        'default': 60,
        'coerce': int,
        'type': 'integer',
        'help_message': 'Timeout for the sagemaker deployment'
    },
    'enable_data_capture': {
        'required': False,
        'default': False,
        'type': 'boolean',
        'help_message': 'Enable data capture for the sagemaker deployment',
    },
    'data_capture_s3_prefix': {
        'required': False,
        'type': 'string',
        'help_message': 'S3 prefix for the data capture for the sagemaker deployment',
    },
    'data_capture_sample_size': {
        'required': False,
        'type': 'integer',
        'coerce': int,
        'help_message': 'Sample size for the data capture for the sagemaker deployment',
        'max': 100,
        'min': 1,
    },
}