import contextlib
import json
import logging
import time
import traceback
from collections.abc import Callable

from starlette.background import BackgroundTasks
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

uviocorn_logger = logging.getLogger("uvicorn.error")
logger = logging.getLogger('app')


def _create_request_log(
        request: Request,
        status_code: int,
        request_body: bytes,
        message: str,
        start_time: float,
        trace: str | None = None,
        error: Exception | None = None,
        ignore_fields: list[str] | None = None
) -> None:
    query_params = dict(request.query_params)
    request_body = json.loads(request_body) if request_body != b'' else {}  # type: ignore
    if ignore_fields:
        for field in ignore_fields:
            with contextlib.suppress(KeyError):
                del request_body[field]  # type: ignore
                del query_params[field]

    data: dict[str, str | int | dict | None] = {
        "user_id": request.query_params.get('user_id', ""),
        "method": request.method,
        "path": request.url.path,
        "client_ip":  request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent", ""),
        "query_params": str(query_params),
        "body": str(request_body),
        "latency": time.time() - start_time
    }
    if error:
        data.update({
            "status_code": status_code,
            "error": str(error),
            "trace": trace[-1000:] if trace else None
        })
        logger.error(message, extra=data)
    else:
        data.update({
            "status_code": status_code
        })
        logger.info(message, extra=data)


class FastApiLoggingMidlleware(BaseHTTPMiddleware):
    def __init__(
            self,
            app: ASGIApp,
            ignore_fields: list[str] | None = None,
            ignore_paths: list[str] | None = None
    ) -> None:
        super().__init__(app)
        self.ignore_fields = ignore_fields
        self.ignore_paths = ignore_paths or ['/metrics', '/openapi.json']

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        if request.url.path in self.ignore_paths:
            return await call_next(request)

        background_tasks = BackgroundTasks()
        request_body = await request.body()

        try:
            response = await call_next(request)
        except Exception as e:
            trace = traceback.format_exc()
            background_tasks.add_task(
                _create_request_log,
                request=request,
                status_code=500,
                start_time=start_time,
                request_body=request_body,
                error=e,
                trace=trace,
                message='Reqest_failed',
                ignore_fields=self.ignore_fields
            )
            logger.error("Exception occurred", exc_info=True)
            return Response(
                status_code=500,
                content="Internal Server Error",
                media_type="text/plain",
                background=background_tasks
            )

        if response.status_code >= 400:
            response_body_chunks = [chunk async for chunk in response.body_iterator]
            response.body_iterator = iterate_in_threadpool(iter(response_body_chunks))
            response_body_bytes = b''.join(response_body_chunks)
            message = response_body_bytes.decode()
        else:
            message = 'Request success'

        background_tasks.add_task(
            _create_request_log,
            request=request,
            start_time=start_time,
            request_body=request_body,
            status_code=response.status_code,
            message=message,
            ignore_fields=self.ignore_fields
        )
        response.background = background_tasks
        return response
