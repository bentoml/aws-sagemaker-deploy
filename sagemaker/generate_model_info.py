import json

DEFAULT_GUNICORN_TIMEOUT = '60'


def generate_model_info(model_name, image_tag, api_name, timeout, num_of_workers):
    model_info = {
        "ContainerHostname": model_name,
        "Image": image_tag,
        "Environment": {
            "API_NAME": api_name,
            "BENTOML_GUNICORN_TIMEOUT": timeout,
            "BENTOML_GUNICORN_NUM_OF_WORKERS":num_of_workers
        },
    }
    return json.dumps(model_info)
