__all__ = []

# import each backend in turn and add to __all__. This syntax
# is explicitly supported by type checkers, while more dynamic
# syntax would not be recognised.
try:
    from fastapi_cacher.base import BaseCache
except ImportError:
    pass
else:
    __all__ += ["BaseCache"]

try:
    from fastapi_cacher.backends.simplecache import SimpleCache
except ImportError:
    pass
else:
    __all__ += ["SimpleCache"]

try:
    from fastapi_cacher.backends.rediscache import RedisCache
except ImportError:
    pass
else:
    __all__ += ["RedisCache"]

try:
    from fastapi_cacher.backends.mongocache import MongoCache
except ImportError:
    pass
else:
    __all__ += ["MongoCache"]

try:
    from fastapi_cacher.backends.memcache import MemCache
except ImportError:
    pass
else:
    __all__ += ["MemCache"]
