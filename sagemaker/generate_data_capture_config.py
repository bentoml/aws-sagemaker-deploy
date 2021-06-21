import json


def generate_data_capture_config(data_capture_sample_percent, data_capture_s3_prefix):
    config = {
        "EnableCapture": True,
        "InitialSamplingPercentage": data_capture_sample_percent,
        "DestinationS3Uri": data_capture_s3_prefix,
        "CaptureOptions": [{"CaptureMode": "Input"}, {"CaptureMode": "Output"},],
    }
    return json.dumps(config)
