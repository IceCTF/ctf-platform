"""
Common Testing Functionality.
"""

import api

from functools import wraps

def clear_cache():
    """
    Clears the cache before the function is run.
    """

    def clear(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            api.cache.clear_all()
            return f(*args, **kwargs)
        return wrapper
    return clear

def ensure_empty_collections(*collections):
    """
    Clears collections listed after function has completed.
    Will throw an assertion if any collection is not empty when called.
    """

    def clear(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            db = api.common.get_conn()
            collection_size = lambda name: len(list(db[name].find()))
            for collection in collections:
                assert collection_size(collection) == 0, "Collection was not empty: " + collection
            result = f(*args, **kwargs)
            return result
        return wrapper
    return clear


def clear_collections(*collections):
    """
    Clears collections listed after function has completed.
    Will throw an assertion if any collection is not empty when called.
    """

    def clear(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            db = api.common.get_conn()
            try:
                result = f(*args, **kwargs)
            finally:
                #Clear the collections.
                for collection in collections:
                    db[collection].remove()
                #Ensure they are then empty.
                for collection in collections:
                    collection_size = lambda collection: len(list(db[collection].find()))
                    assert collection_size(collection) == 0, "Collection: {} was not able to be cleared.".format(collection)
            return result
        return wrapper
    return clear
