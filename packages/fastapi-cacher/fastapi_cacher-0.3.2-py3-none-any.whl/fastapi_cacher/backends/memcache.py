import ast
from dataclasses import asdict, dataclass
from typing import Optional, Tuple

from aiomcache import Client
from fastapi_cacher.base import BaseCache


@dataclass
class Value:
    """
    A data class for storing cached data along with its expiration timestamp.

    Attributes:
        data (bytes): The cached data.
        ttl_ts (int): The time-to-live expiration timestamp of the cached data.
    """
    data: bytes
    ttl_ts: int


class MemCache(BaseCache):
    def __init__(self, host: str, port: int, threshold: int, default_timeout: int):
        """
        Initializes the cache with a given threshold and default timeout.
        Parameters:
            threshold (int): The maximum number of items to store before eviction.
            default_timeout (int): The default time-to-live (TTL) for each cache item, in seconds.
        """
        self._client = Client(host, port)
        self._threshold = threshold
        self._default_timeout = default_timeout

    async def get_with_ttl(self, key: str) -> Tuple[int, Optional[bytes]]:
        """
        Retrieve a value and its TTL from the cache.

        Parameters:
            key (str): The key to retrieve.

        Returns:
            Tuple[int, Optional[bytes]]: A tuple of the TTL and the value, or None if not found.
        """
        value = await self._client.get(key.encode())
        if value:
            value_dict = ast.literal_eval(value.decode())  # Decode the byte string to a regular string
            value_obj = Value(**value_dict)  # Create a Value object from the dictionary
            return value_obj.ttl_ts, value_obj.data
        return self._default_timeout, None

    async def get(self, key: str) -> Optional[bytes]:
        """
        Retrieve a value from the cache.

        Parameters:
            key (str): The key to retrieve.

        Returns:
            Optional[bytes]: The value, or None if not found.
        """
        value = await self._client.get(key.encode())
        if value:
            value_dict = ast.literal_eval(value.decode())
            return value_dict["data"]
        return None

    async def set(self, key: str, value: bytes, expire: Optional[int] = None) -> None:
        """
        Set a value in the cache.

        Parameters:
            key (str): The key to set.
            value (bytes): The value to store.
            expire (Optional[int]): The time-to-live (TTL) for the cache item, in seconds.
        """
        keys_count = await self._get_keys_count()
        if keys_count >= self._threshold:
            await self._evict()

        ttl_ts = expire or self._default_timeout
        value_obj = Value(data=value, ttl_ts=ttl_ts)
        value_dict = asdict(value_obj)
        value_dict = str(value_dict).encode()
        key = key.encode()
        await self._client.set(key, value_dict, exptime=ttl_ts)

    async def clear(self, key: Optional[str] = None) -> int:
        """
        Clear items from the cache.

        Parameters:
            key (Optional[str]): The specific key to clear.
            flush (bool): If True, flush the entire cache.

        Returns:
            int: The number of items cleared.
        """

        if key is not None:
            return await self._client.delete(key.encode())

        else:  # Flush the entire cache
            return await self._client.flush_all()

    def __repr__(self) -> str:
        return f"MemcachedCache(threshold={self._threshold}, default_timeout={self._default_timeout})"

    async def _get_keys_count(self) -> int:
        """
        Get the count of keys in the cache.

        Returns:
            int: The number of keys in the cache.
        """
        stats = await self._client.stats()
        return int(stats[b'curr_items'][0])

    async def _evict(self) -> None:
        """
        Evict the least recently used item from the cache.
        """
        # Assuming the `stats` command returns the items in LRU order
        stats = await self._client.stats('items')
        if stats:
            slabs = stats.keys()
            for slab in slabs:
                item_stats = await self._client.stats(f'cachedump {slab.decode()} 1')
                if item_stats:
                    first_key = next(iter(item_stats.keys()))
                    await self._client.delete(first_key)
                    break
