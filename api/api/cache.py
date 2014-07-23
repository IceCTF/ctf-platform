"""
Caching Library for picoCTF API
"""

from functools import wraps
from bson import json_util

import api
import redis

from api.common import InternalException

log = api.logger.use(__name__)

redis_host = "127.0.0.1"
redis_port = 6379

no_cache = False

cache = redis.StrictRedis(host=redis_host, port=redis_port, db=0)
fast_cache = {}

def clear_all():
    """
    Clears the cache.
    """
    cache.flushdb()
    fast_cache.clear()

def get_key(f, *args, **kwargs):
    """
    Returns a unique key for a memoized function.

    Args:
        f: the function
        args: positional arguments
        kwargs: keyword arguments
    Returns:
        The key.
    """

    key = "{}.{}${}${}".format(f.__module__, f.__name__, str(args), str(kwargs)).replace(" ", "~")

    return key

def get(key, deserialize=True):
    """
    Get a key from the cache.

    Args:
        key: cache key
        deserialize: Whether or not the data should be deserialized.
    Returns:
        The result deserialized.
    """

    cached_result = cache.get(key)

    if deserialize and cached_result is not None:
        cached_result = json_util.loads(cached_result.decode("utf-8"))

    return cached_result

def set(key, value, timeout=None, serialize=True):
    """
    Set a key in the cache.

    Args:
        key: The cache key.
        timeout: Time the key is valid.
        serialize: Whether or not the data should be serialized.
    """

    if serialize:
        value = json_util.dumps(value)

    if timeout:
        cache.setex(key, timeout, value)
    else:
        cache.set(key, value)


def fast_memoize():
    """
    Cache a function based on its arguments.

    Args:
        timout: Time the result stays valid in the cache.
    Returns:
        The functions result.
    """

    def decorator(f):
        """
        Inner decorator
        """

        @wraps(f)
        def wrapper(*args, **kwargs):
            """
            Function cache
            """

            key = get_key(f, *args, **kwargs)

            cached_result = fast_cache.get(key)

            if cached_result is None or no_cache:
                function_result = f(*args, **kwargs)

                fast_cache[key] = function_result
                return function_result

            return cached_result

        return wrapper

    return decorator

def invalidate_fast_memoization(f, *args, **kwargs):
    """
    Invalidate a memoized function.

    Args:
        f: the function
        You must pass all arguments given to the function to accurately invalidate it.
    """

    key = get_key(f, *args, **kwargs)
    fast_cache.pop(key, None)

def memoize(timeout=None, serialize=True, deserialize=True):
    """
    Cache a function based on its arguments.

    Args:
        timout: Time the result stays valid in the cache.
    Returns:
        The functions result.
    """

    def decorator(f):
        """
        Inner decorator
        """

        @wraps(f)
        def wrapper(*args, **kwargs):
            """
            Function cache
            """

            key = get_key(f, *args, **kwargs)

            cached_result = get(key, deserialize=deserialize)

            if cached_result is None or no_cache:
                function_result = f(*args, **kwargs)

                set(key, function_result, timeout=timeout, serialize=serialize)
                return function_result

            return cached_result

        return wrapper

    return decorator

def invalidate_memoization(f, *args, **kwargs):
    """
    Invalidate a memoized function.

    Args:
        f: the function
        You must pass all arguments given to the function to accurately invalidate it.
    """

    key = get_key(f, *args, **kwargs)
    cache.delete(key)

