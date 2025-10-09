from typing import Literal, get_args, Final, Optional

from fastapi_cacher.coder import JsonCoder, Coder
from pydantic import BaseModel, model_validator, field_validator

SUPPORTED_CACHE_TYPES = Literal["SimpleCache", "RedisCache", "MongoCache", "MemCache"]


class CacheConfig(BaseModel):
    cache_type: SUPPORTED_CACHE_TYPES = "SimpleCache"
    default_timeout: int = 300
    app_space: str = "fastapi-cacher"
    coder: Coder = JsonCoder  # if you need an instance, use JsonCoder()
    sliding_expiration: bool = False  # reset expiration on every access

    ONE_HOUR: Final[int] = 3600
    ONE_DAY: Final[int] = ONE_HOUR * 24
    ONE_WEEK: Final[int] = ONE_DAY * 7
    ONE_MONTH: Final[int] = ONE_DAY * 30
    ONE_YEAR: Final[int] = ONE_DAY * 365

    simple_cache_threshold: int = 100

    # Redis
    redis_url: str = ""
    redis_host: Optional[str] = None
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_db: int = 0

    # Mongo
    mongo_url: str = ""
    mongo_database: str = "fastapi-cacher"
    mongo_collection: str = "cache"
    mongo_direct_connection: bool = False

    # Memcache
    memcache_host: str = ""
    memcache_port: int = 11211
    memcache_threshold: int = 100

    @field_validator("cache_type")
    @classmethod
    def validate_cache_type(cls, value: str) -> str:
        """Validate that the cache_type is supported."""
        if value not in get_args(SUPPORTED_CACHE_TYPES):
            raise ValueError(f"cache_type must be one of {get_args(SUPPORTED_CACHE_TYPES)}")
        return value

    @model_validator(mode="after")
    def validate_connection_attributes(self) -> "CacheConfig":
        if self.cache_type == "RedisCache":
            # Either a full URL OR both host & password must be provided
            if not self.redis_url and not (self.redis_host and self.redis_password):
                raise ValueError(
                    "With RedisCache, either redis_url must be provided or "
                    "(redis_host, redis_password) must be provided."
                )

        elif self.cache_type == "MongoCache":
            if not self.mongo_url:
                raise ValueError("With MongoCache, mongo_url must be provided.")

        elif self.cache_type == "MemCache":
            if not self.memcache_host:
                raise ValueError("With MemCache, memcache_host must be provided.")

        return self

    class Config:
        arbitrary_types_allowed = True
