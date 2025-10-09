import logging

from graypy import GELFUDPHandler  # type: ignore
from starlette.applications import Starlette

from logging_midlleware.fastapi_midlleware import FastApiLoggingMidlleware


def setup_logger(
        app: Starlette,
        host: str,
        port: int,
        source: str,
        ignore_fields: list[str] | None = None,
        ignore_paths: list[str] | None = None
) -> None:
    logger = logging.getLogger('app')
    logger.setLevel(logging.INFO)
    handler = GELFUDPHandler(host, port, localname=source)
    logger.addHandler(handler)
    app.add_middleware(
        FastApiLoggingMidlleware,
        ignore_fields=ignore_fields,
        ignore_paths=ignore_paths
    )
