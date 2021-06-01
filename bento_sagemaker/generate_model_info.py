import sys
import json

DEFAULT_GUNICORN_TIMEOUT = '60'


if __name__ == '__main__':
    model_info = {
        "ContainerHostname": sys.argv[1],
        "Image": sys.argv[2],
        "Environment": {
            "API_NAME": sys.argv[3],
            "BENTOML_GUNICORN_TIMEOUT": DEFAULT_GUNICORN_TIMEOUT,
        },
    }
    print(json.dumps(model_info))
