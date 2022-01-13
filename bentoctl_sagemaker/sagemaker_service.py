from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from starlette.types import ASGIApp, Scope, Receive, Send
import bentoml

AWS_SAGEMAKER_SERVE_PORT = 8080
AWS_CUSTOM_ENDPOINT_HEADER = "X-Amzn-SageMaker-Custom-Attributes"
BENTOML_HEALTH_CHECK_PATH = "/livez"
svc = bentoml.load(".", working_dir='.')


class SagemakerMiddleware:
    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        req = Request(scope, receive)
        if req.url.path == "/ping":
            scope["path"] = BENTOML_HEALTH_CHECK_PATH

        if req.url.path == "/invocations":
            assert AWS_CUSTOM_ENDPOINT_HEADER in req.headers
            api_path = req.headers[AWS_CUSTOM_ENDPOINT_HEADER]
            scope["path"] = "/" + api_path

        await self.app(scope, receive, send)
        return


svc.add_asgi_middleware(SagemakerMiddleware)
