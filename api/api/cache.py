"""
Caching Library for picoCTF API
"""

from functools import wraps
from bson import json_util, datetime

import api
import time

log = api.logger.use(__name__)

no_cache = False
fast_cache = {}
_mongo_index = None

def clear_all():
    """
    Clears the cache.
    """
    db = api.common.get_conn()
    db.cache.remove()
    fast_cache.clear()

def get_mongo_key(f, *args, **kwargs):
    """
    Returns a mongo object key for the function.

    Args:
        f: the function
        args: positional arguments
        kwargs: keyword arguments
    Returns:
        The key.
    """

    min_kwargs = dict(filter(lambda pair: pair[1] is not None, kwargs.items()))

    return {
        "function": "{}.{}".format(f.__module__, f.__name__),
        "args": args,
        "kwargs": min_kwargs,
    }

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

    if len(args) > 0:
        kwargs["#args"] = ",".join(map(str, args))

    sorted_keys = sorted(kwargs)
    arg_key = "&".join(["{}:{}".format(key, kwargs[key]) for key in sorted_keys])

    key = "{}.{}${}".format(f.__module__, f.__name__, arg_key).replace(" ", "~")

    return key

def get(key):
    """
    Get a key from the cache.

    Args:
        key: cache key
        deserialize: Whether or not the data should be deserialized.
    Returns:
        The result deserialized.
    """

    db = api.common.get_conn()

    cached_result = db.cache.find_one(key)

    if cached_result:
        return cached_result["value"]

def set(key, value, timeout=None):
    """
    Set a key in the cache.

    Args:
        key: The cache key.
        timeout: Time the key is valid.
        serialize: Whether or not the data should be serialized.
    """

    db = api.common.get_conn()

    update = key.copy()
    update.update({"value":value})

    if timeout is not None:
        expireAt = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
        update.update({"expireAt": expireAt})

    db.cache.update(key, update, upsert=True)

def fast_memoize(timeout=0):
    """
    Cache a function based on its arguments.

    Args:
        timeout: Time the result stays valid in the cache.
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

            if cached_result is None or no_cache or int(time.time()) - cached_result["set_time"] > timeout:
                function_result = f(*args, **kwargs)

                fast_cache[key] = {
                    "result": function_result,
                    "timeout": timeout,
                    "set_time": int(time.time())
                }

                return function_result

            return cached_result["result"]

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

def memoize(timeout=None, fast=False):
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

            if not kwargs.get("cache", True):
                kwargs.pop("cache", None)
                return f(*args, **kwargs)

            key = get_mongo_key(f, *args, **kwargs)

            cached_result = get(key)

            if cached_result is None or no_cache:
                function_result = f(*args, **kwargs)
                set(key, function_result, timeout=timeout)

                return function_result

            return cached_result

        return wrapper

    return decorator

def invalidate_memoization(f, *keys):
    """
    Invalidate a memoized function.

    Args:
        f: the function
        You must pass all arguments given to the function to accurately invalidate it.
    """

    db = api.common.get_conn()

    search = {"function": "{}.{}".format(f.__module__, f.__name__)}
    search.update({"$or": list(keys)})

    db.cache.remove(search)
