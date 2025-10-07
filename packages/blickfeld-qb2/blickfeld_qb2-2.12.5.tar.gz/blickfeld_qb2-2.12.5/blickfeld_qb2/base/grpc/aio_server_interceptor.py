import sys

sys.path.insert(0, "/usr/lib")

import asyncio
import logging
import time
from collections.abc import AsyncGenerator, AsyncIterator, Callable

from google.protobuf.any_pb2 import Any
from grpc.aio import AioRpcError, ServicerContext
from grpc_interceptor import AsyncServerInterceptor

from blickfeld.base.grpc.base_error import BaseError

logger = logging.getLogger("server")


class AioServerInterceptor(AsyncServerInterceptor):
    async def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        context: ServicerContext,
        method_name: str,
    ) -> AsyncGenerator[Any] | Any | None:
        start_ts = time.monotonic()
        try:
            response_or_iterator = method(request_or_iterator, context)
            if not hasattr(response_or_iterator, "__aiter__"):
                # Unary, just await and return the response
                response = await response_or_iterator
                logger.info(f"Request: {method_name} [{int((time.monotonic() - start_ts) * 1e3)}ms]")
                return response
        except (BaseError, AioRpcError) as e:
            e = BaseError.create_from_exception(e)
            logger.warning(f"Request: {method_name} [{int((time.monotonic() - start_ts) * 1e3)}ms, {e.code.name}]")
            await context.abort(e.code, e.message or "")
            return None

        logger.info(f"Stream request: {method_name}")
        # Server streaming responses, delegate to an async generator helper.
        # Note that we do NOT await this.
        return self._intercept_streaming(method_name, start_ts, response_or_iterator, context)

    async def _intercept_streaming(
        self, method_name: str, start_ts: float, iterator: AsyncIterator[Any], context: ServicerContext
    ) -> AsyncGenerator[Any]:
        try:
            async for r in iterator:
                yield r
        except (BaseError, AioRpcError) as e:
            e = BaseError.create_from_exception(e)
            logger.warning(
                f"Stream request: {method_name} [{int((time.monotonic() - start_ts) * 1e3)}ms, {e.code.name}]"
            )
            await context.abort(e.code, e.message or "")
        except asyncio.CancelledError:
            logger.info(f"Stream request: {method_name} [{int((time.monotonic() - start_ts) * 1e3)}ms]")
            raise
