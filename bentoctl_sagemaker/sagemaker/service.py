import bentoml
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.types import ASGIApp, Receive, Scope, Send

AWS_SAGEMAKER_SERVE_PORT = 8080
AWS_CUSTOM_ENDPOINT_HEADER = "X-Amzn-SageMaker-Custom-Attributes"
BENTOML_HEALTH_CHECK_PATH = "/livez"

# use standalone_load so that the path is not changed back
# after loading.
svc = bentoml.load(".", standalone_load=True)


class SagemakerMiddleware:
    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            req = Request(scope, receive)
            if req.url.path == "/ping":
                scope["path"] = BENTOML_HEALTH_CHECK_PATH

            if req.url.path == "/invocations":
                assert AWS_CUSTOM_ENDPOINT_HEADER in req.headers
                api_path = req.headers[AWS_CUSTOM_ENDPOINT_HEADER]
                scope["path"] = "/" + api_path

        await self.app(scope, receive, send)


svc.add_asgi_middleware(SagemakerMiddleware)
