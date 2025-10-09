import inspect
import logging
import warnings
from functools import wraps
from inspect import iscoroutinefunction
from typing import Callable, Any

from fastapi import HTTPException, Response, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.dependencies.utils import get_typed_return_annotation
from fastapi_cacher.backends import BaseCache
from fastapi_cacher.config import CacheConfig
from fastapi_cacher.utils import key_builder, run_coro_in_background

__all__ = ["Cache", "CacheConfig"]
logger: logging.Logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def _get_request_and_response(func: Callable, args: tuple, kwargs: dict) -> tuple:
    sig = inspect.signature(func)
    params = sig.parameters

    request = None
    response = None
    request_param_name = None
    response_param_name = None

    # Match positional arguments with their names in the function signature
    for name, arg in zip(params.keys(), args):
        if isinstance(arg, Request):
            request = arg
            request_param_name = name
        elif isinstance(arg, Response):
            response = arg
            response_param_name = name

    # If request/response not found in args, look in kwargs
    if not request or not response:
        for name, kwarg in kwargs.items():
            if isinstance(kwarg, Request):
                request = kwarg
                request_param_name = name
            elif isinstance(kwarg, Response):
                response = kwarg
                response_param_name = name

    return request, response, request_param_name, response_param_name


class Cache:
    def __init__(self, config: CacheConfig = CacheConfig()) -> None:
        self._config = config
        self._coder = self._config.coder
        self._backend_cache = self._get_cache_backend()

    def _get_cache_backend(self) -> BaseCache:
        cache_type = self._config.cache_type
        if cache_type == 'SimpleCache':
            warnings.warn("SimpleCache is not recommended for production environment with multiple workers.")
            from fastapi_cacher.backends import SimpleCache
            return SimpleCache(
                threshold=self._config.simple_cache_threshold,
                default_timeout=self._config.default_timeout
            )

        if cache_type == 'RedisCache':
            from fastapi_cacher.backends import RedisCache
            return RedisCache(
                url=self._config.redis_url,
                host=self._config.redis_host,
                port=self._config.redis_port,
                password=self._config.redis_password,
                db=self._config.redis_db,
                app_space=self._config.app_space,
                default_timeout=self._config.default_timeout
            )

        if cache_type == 'MongoCache':
            from fastapi_cacher.backends import MongoCache
            return MongoCache(
                url=self._config.mongo_url,
                database=self._config.mongo_database,
                collection=self._config.mongo_collection,
                direct_connection=self._config.mongo_direct_connection,
                app_space=self._config.app_space,
                default_timeout=self._config.default_timeout
            )

        if cache_type == 'MemCache':
            from fastapi_cacher.backends import MemCache
            return MemCache(
                host=self._config.memcache_host,
                port=self._config.memcache_port,
                threshold=self._config.memcache_threshold,
                default_timeout=self._config.default_timeout
            )

    async def _cache_result(self, result_encoded, key, timeout) -> None:
        try:
            await self.set(key, result_encoded, timeout)
        except Exception as e:
            logger.warning(
                f"Error setting cache key '{key}' in backend: {e}",
                exc_info=True,
            )

    def _get_is_sliding_expiration(self, endpoint_sliding_expiration: bool | None) -> bool:
        """
        Check if the endpoint has sliding expiration enabled, if yes, return its value over the global config.
        """
        if endpoint_sliding_expiration is None and self._config.sliding_expiration:
            return True
        return endpoint_sliding_expiration or False

    def cached(self,
               timeout: int = None,
               sliding_expiration: bool = None,
               namespace: str = "",
               query_params: bool = True,
               json_body: bool = False,
               require_auth_header: bool = False) -> Callable[[Callable], Callable]:
        """
        Decorator to cache the result of a function.
        :param timeout : Timeout in seconds (int).
                  Set to `0` to never expire. If not specified, the default timeout from the cache config is used.
                  A pre-calculated values in the cache_config can be used, e.g., `cache_config.ONE_HOUR`,
                  `cache_config.ONE_DAY`, etc.
        :param sliding_expiration : Enable sliding expiration for the cache key (bool).
                  sliding window expiration mechanism resets the expiration time on every access
                  to the cache key, this means that the cache key will only expire if it is not accessed
                  for the duration of the timeout.

                  * sliding_expiration at the endpoint level takes precedence over the global config.

        :param namespace: Namespace for the cache keys.
        :param query_params: Include query parameters in the cache key.
        :param json_body: Include the request JSON body in the cache key.
        :param require_auth_header: Include the Authorization header in the cache string key.
                  If set to True, the Authorization header is required in the request
                  and if not present - Raises `HTTPException(401)`.
        """

        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                async def ensure_async_func(*func_args, **func_kwargs) -> Any:
                    """Run cached sync functions in thread pool just like FastAPI."""
                    if iscoroutinefunction(func):
                        # async, return as is.
                        return await func(*func_args, **func_kwargs)
                    else:
                        # sync, wrap in thread and return async
                        return await run_in_threadpool(func, *func_args, **func_kwargs)  # type: ignore[arg-type]

                is_sliding_expiration = self._get_is_sliding_expiration(sliding_expiration)

                request, response, request_param_name, response_param_name = _get_request_and_response(
                    func=func,
                    args=args,
                    kwargs=kwargs
                )

                if request and request.method != 'GET':
                    raise Exception("Cached decorator can only be used with GET requests.")

                return_type = get_typed_return_annotation(func)
                auth_header = ""
                if require_auth_header:
                    auth_header = request.headers.get("Authorization")
                    if not auth_header:
                        raise HTTPException(status_code=401, detail="Not authorized.")

                key = await key_builder(
                    func,
                    auth_header=auth_header,
                    app_space=self._config.app_space,
                    namespace=namespace,
                    request=request,
                    args=args,
                    kwargs=kwargs,
                    request_param_name=request_param_name,
                    response_param_name=response_param_name,
                    query_params=query_params,
                    json_body=json_body
                )
                try:
                    ttl, cached_result = await self.get_with_ttl(key)
                except Exception as e:
                    logger.warning(
                        f"Error retrieving cache key '{key}' from backend: {e}",
                        exc_info=True,
                    )
                    ttl, cached_result = 0, None

                if cached_result is not None:  # cache hit
                    result = self._coder.decode_as_type(cached_result, type_=return_type)
                    if is_sliding_expiration:
                        run_coro_in_background(self._cache_result(
                            result_encoded=cached_result,
                            key=key,
                            timeout=timeout or self._config.default_timeout
                        ))
                    if response:
                        response.headers['X-Cache-Hit'] = 'true'
                        response.headers['X-Cache-Key'] = key
                        response.headers['X-Cache-TTL'] = str(ttl)

                else:  # cache miss
                    result = await ensure_async_func(*args, **kwargs)
                    result_encoded = self._coder.encode(result)
                    run_coro_in_background(self._cache_result(
                        result_encoded=result_encoded,
                        key=key,
                        timeout=timeout or self._config.default_timeout
                    ))
                    if response:
                        response.headers['X-Cache-Hit'] = 'false'
                        response.headers['X-Cache-Key'] = key
                        response.headers['X-Cache-TTL'] = str(timeout or self._config.default_timeout)
                return result

            return wrapper

        return decorator

    async def get_with_ttl(self, key: str) -> tuple[int, bytes | None]:
        return await self._backend_cache.get_with_ttl(key)

    async def get(self, key: str) -> bytes | None:
        return await self._backend_cache.get(key)

    async def set(self, key: str, value: bytes, expire: int = None) -> None:
        await self._backend_cache.set(key, value, expire)

    async def clear(self, namespace: str = None, key: str = None) -> int:
        if self._config.cache_type == 'MemCache':
            return await self._backend_cache.clear(key)
        return await self._backend_cache.clear(namespace, key)
