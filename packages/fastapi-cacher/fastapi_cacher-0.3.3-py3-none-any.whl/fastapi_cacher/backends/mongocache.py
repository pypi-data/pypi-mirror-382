import datetime
import warnings
from typing import Optional, Tuple
from urllib.parse import urlparse

import pymongo
from fastapi_cacher.base import BaseCache
from motor.motor_asyncio import AsyncIOMotorClient


class MongoCache(BaseCache):
    """
    MongoDB backend provider

    This backend requires an existing database and collection within your MongoDB environment to be passed during
    backend init. If ttl is going to be used, an index on the ttl field should be manually enabled on the collection.
    MongoDB will take care of deleting outdated objects, but this is not instant so don't be alarmed when they linger
    around for a bit.
    """

    def __init__(self,
                 url: str,
                 database: Optional[str],
                 collection: str,
                 direct_connection: bool,
                 app_space: str | None,
                 default_timeout: int | None) -> None:
        """
        Direct connection is used to bypass the MongoDB driver's automatic reconnection mechanism.
        """
        # Parse the URI to extract the database name if not provided
        parsed_uri = urlparse(url)
        url_database_name = parsed_uri.path[1:] if parsed_uri.path else None

        if url_database_name and database and url_database_name != database:
            warnings.warn(f"MongoCache - Database name provided in the URL '{url_database_name}' does not match "
                          f"the one provided as a parameter '{database}'."
                          " Using the one provided in the URL!")

        self.database_name = url_database_name or database

        if not self.database_name:
            raise ValueError("Database name must be provided either in the URI or as a parameter")

        self._client = pymongo.MongoClient(url, directConnection=direct_connection)
        self._client_async = AsyncIOMotorClient(url, directConnection=direct_connection)
        self._database = self._client_async[self.database_name]
        self._collection = self._database[collection]
        self._default_timeout = default_timeout
        self._app_space = app_space
        self._init()

    def _init(self) -> None:
        collection = self._client[self.database_name][self._collection.name]
        indexes = collection.index_information()
        index_exists = any(index['key'] == [('ttl', pymongo.ASCENDING)] for index in indexes.values())
        if not index_exists:
            collection.create_index("ttl", expireAfterSeconds=self._default_timeout)

    async def close(self) -> None:
        self._client_async.close()

    async def get_with_ttl(self, key: str) -> Tuple[int, Optional[bytes]]:
        document = await self._collection.find_one({"key": key})

        if document:
            value = document.get("value")
            ttl = document.get("ttl")

            if not ttl:
                return -1, value

            # Check the TTL ourselves
            expire = int(ttl.timestamp()) - int(datetime.datetime.utcnow().timestamp())
            if expire > 0:
                return expire, value

        return 0, None

    async def get(self, key: str) -> Optional[bytes]:
        document = await self._collection.find_one({"key": key})
        if document:
            return document.get("value")
        return None

    async def set(self, key: str, value: bytes, expire: Optional[int] = None) -> None:
        ttl = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=expire if expire is not None else self._default_timeout)

        await self._collection.update_one(
            {"key": key},
            {"$set": {"key": key, "value": value, "ttl": ttl}},
            upsert=True,
        )

    async def clear(self, namespace: Optional[str] = None, key: Optional[str] = None) -> int:
        if key:
            result = await self._collection.delete_many({"key": key})
            return result.deleted_count

        pattern = ""
        if self._app_space:
            pattern += f"{self._app_space}:"
        if namespace:
            pattern += f"{namespace}:"

        result = await self._collection.delete_many({"key": {"$regex": pattern}})
        return result.deleted_count
