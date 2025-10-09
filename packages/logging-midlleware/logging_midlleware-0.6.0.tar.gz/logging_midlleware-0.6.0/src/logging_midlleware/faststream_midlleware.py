import json
import logging
import traceback
from typing import Any

from faststream import BaseMiddleware
from faststream.broker.message import StreamMessage
from faststream.types import AsyncFuncAny

logger = logging.getLogger('app')


def _create_msg_log(
    msg_body: bytes,
    message_log: str,
    trace: str | None = None,
    error: Exception | None = None
) -> None:
    data = json.loads(msg_body.decode())
    if error:
        data.update({
            'error': str(error),
            'trace': trace[-1000:] if trace else None
        })
        logger.error(message_log, extra=data)
    else:
        logger.info(message_log, extra=data)


class FastStreamLoggingMidlleware(BaseMiddleware):
    async def consume_scope(
        self,
        call_next: AsyncFuncAny,
        msg: StreamMessage[Any],
    ) -> Any:
        try:
            res = await call_next(msg)
            _create_msg_log(msg.body, 'Msg success')
            return res
        except Exception as e:
            _create_msg_log(
                msg_body=msg.body,
                message_log='Msg failed',
                error=e,
                trace=traceback.format_exc()
            )
            return None

