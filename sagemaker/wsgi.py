# Copyright 2019 Atalaya Tech, Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging

from bentoml import load_from_dir
from bentoml.types import HTTPRequest
from flask import Flask, Response, request


def setup_bento_service_api_route(app, bento_service):
    def view_function():
        req = HTTPRequest.from_flask_request(request)
        api = bento_service.get_inference_api(
            request.headers.get("X-Amzn-SageMaker-Custom-Attributes")
        )
        response = api.handle_request(req)
        return response.to_flask_response()

    app.add_url_rule(
        rule="/invocations",
        endpoint="invocations",
        view_func=view_function,
        methods=["POST"],
    )


def ping_view_func():
    return Response(response="\n", status=200, mimetype="application/json")


def setup_routes(app, bento_service):
    """
    Setup routes required for AWS sagemaker
    /ping
    /invocations
    """
    app.add_url_rule("/ping", "ping", ping_view_func)
    setup_bento_service_api_route(app, bento_service)


# AWS Sagemaker requires custom inference docker container to implement a web server
# that responds to /invocations and /ping on port 8080.
AWS_SAGEMAKER_SERVE_PORT = 8080


class BentomlSagemakerServer:
    """
    BentomlSagemakerServer create an AWS Sagemaker compatibility REST API model server
    """

    def __init__(self, bento_service, app_name=None):
        app_name = bento_service.name if app_name is None else app_name

        self.bento_service = bento_service
        self.app = Flask(app_name)
        setup_routes(self.app, self.bento_service)

    def start(self):
        self.app.run(port=AWS_SAGEMAKER_SERVE_PORT)


model_service = load_from_dir("/bento")
server = BentomlSagemakerServer(model_service)
app = server.app
