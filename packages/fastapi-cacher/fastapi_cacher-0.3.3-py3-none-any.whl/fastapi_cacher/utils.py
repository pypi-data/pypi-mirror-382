import asyncio
import hashlib
from typing import Any, Callable, Dict, Optional, Tuple

from starlette.requests import Request


async def key_builder(
        func: Callable[..., Any],
        auth_header: str,
        app_space: str,
        namespace: str = "",
        *,
        request: Optional[Request] = None,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
        request_param_name: str,
        response_param_name: str,
        query_params: bool,
        json_body: bool
) -> str:
    kwargs_copy = kwargs.copy()
    kwargs_copy.pop(request_param_name)
    kwargs_copy.pop(response_param_name)
    sorted_kwargs = tuple(sorted(kwargs_copy.items()))
    request_details = ""
    if request:
        if query_params:
            request_details = str(sorted(request.query_params.items()))
        if json_body:
            try:
                # Check if Content-Length is not zero
                if request.headers.get('Content-Length', '0') != '0':
                    json_body = await request.json()
                    if json_body:
                        request_details += str(json_body)
            except Exception as e:
                print('Error reading JSON body for cache:', e)

    key_str = f"{func.__name__}:{auth_header}:{args}:{sorted_kwargs}:{request_details}"
    key_hash = hashlib.md5(key_str.encode()).hexdigest()
    key = f"{app_space}:{namespace}:{key_hash}"
    return key


def run_coro_in_background(coro):
    asyncio.create_task(coro)
