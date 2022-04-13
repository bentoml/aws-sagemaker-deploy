operator_schema = {
    "region": {"required": True, "type": "string", "help_message": "AWS region"},
    "instance_type": {
        "required": True,
        "default": "ml.t2.medium",
        "type": "string",
        "help_message": "Instance type for the sagemaker deployment",
    },
    "initial_instance_count": {
        "default": 1,
        "type": "integer",
        "coerce": int,
        "required": True,
        "help_message": "Initial instance count for the sagemaker deployment",
    },
    "timeout": {
        "required": False,
        "default": 60,
        "coerce": int,
        "type": "integer",
        "help_message": "Timeout for the sagemaker deployment",
    },
}

data_capture_schema = {
    "enable_data_capture": {
        "required": False,
        "default": False,
        "type": "boolean",
        "coerce": bool,
        "help_message": "Enable data capture for the sagemaker deployment",
    },
    "destination_s3_uri": {
        "required": False,
        "default": "",
        "type": "string",
        "help_message": "S3 URI for the data capture for the sagemaker deployment",
    },
    "initial_sampling_percentage": {
        "required": False,
        "type": "integer",
        "default": "1",
        "coerce": int,
        "help_message": "Percentage of the data capture for the sagemaker deployment. Value between 0 and 100",
        "max": 100,
        "min": 1,
    },
}

OPERATOR_SCHEMA = {**operator_schema, **data_capture_schema}
