import asyncio
from contextlib import asynccontextmanager
import logging
from types import SimpleNamespace
from aiohttp import ClientSession, TraceConfig, TraceRequestEndParams, TraceRequestStartParams

logger = logging.getLogger(__name__)


@asynccontextmanager
async def make_session():
    headers = {
        "appuid": "ZET.Mobile",
        "x-tenant": "KingICT_ZET_Public",
        "User-Agent": "okhttp/4.9.2",
    }

    async with ClientSession(
        base_url="https://api.zet.hr",
        headers=headers,
        trace_configs=[logger_trace_config()],
    ) as session:
        yield session


def logger_trace_config() -> TraceConfig:
    async def on_request_start(
        _: ClientSession,
        context: SimpleNamespace,
        params: TraceRequestStartParams,
    ):
        context.start = asyncio.get_event_loop().time()
        logger.debug(f"--> {params.method} {params.url}")

    async def on_request_end(
        _: ClientSession, context: SimpleNamespace, params: TraceRequestEndParams
    ):
        elapsed = round(100 * (asyncio.get_event_loop().time() - context.start))
        logger.debug(f"<-- {params.method} {params.url} HTTP {params.response.status} {elapsed}ms")

    trace_config = TraceConfig()
    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_end.append(on_request_end)
    return trace_config
