""" The common module contains general-purpose functions potentially used by multiple modules in the system."""
__author__ = ["Collin Petty", "Peter Chapman", "Jonathan Burket"]
__copyright__ = "Carnegie Mellon University"
__license__ = "MIT"
__maintainer__ = ["Collin Petty", "Peter Chapman", "Jonathan Burket"]
__email__ = ["collin@cmu.edu", "peter@cmu.edu", "jburket@cmu.edu"]
__status__ = "Production"

import uuid

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, InvalidName
from werkzeug.contrib.cache import SimpleCache
from voluptuous import Invalid, MultipleInvalid
from hashlib import md5

allowed_protocols = []
allowed_ports = []

cache = SimpleCache()
admin_emails = None

__connection = None
__client = None

mongo_addr = "127.0.0.1"
mongo_port = 27017
mongo_db_name = ""

external_client = None

def get_conn():
    """
    Get a database connection

    Ensures that only one global database connection exists per thread.
    If the connection does not exist a new one is created and returned.
    """

    if external_client is not None:
        return external_client

    global __client, __connection
    if not __connection:
        try:
            __client = MongoClient(mongo_addr, mongo_port)
            __connection = __client[mongo_db_name]
        except ConnectionFailure:
            raise SevereInternalException("Could not connect to mongo database {} at {}:{}".format(mongo_db_name, mongo_addr, mongo_port))
        except InvalidName as error:
            raise SevereInternalException("Database {} is invalid! - {}".format(mongo_db_name, error))

    return __connection


def esc(s):
    """
    Escapes a string to prevent html injection

    Returns a string with special HTML characters replaced.
    Used to sanitize output to prevent XSS. We looked at 
    alternatives but there wasn't anything of an appropriate 
    scope that we could find. In the long-term this should be 
    replaced with a proper sanitization function written by 
    someone else."""
    return s\
        .replace('&', '&amp;')\
        .replace('<', '&lt;')\
        .replace('>', '&gt;')\
        .replace('"', '&quot;')\
        .replace("'", '&#39;')

def token():
    """
    Generate a token, should be random but does not have to be secure necessarily. Speed is a priority.

    Returns:
        The randomly generated token
    """

    return str(uuid.uuid4().hex)

def hash(string):
    """
    Hashes a string

    Args:
        string: string to be hashed.
    Returns:
        The hex digest of the string.
    """

    return md5(string.encode("utf-8")).hexdigest()

class APIException(Exception):
    """
    Exception thrown by the API.
    """

    pass

def WebSuccess(message=None, data=None):
    """
    Successful web request wrapper.
    """

    return {
        "status": 1,
        "message": message,
        "data": data
    }

def WebError(message=None, data=None):
    """
    Unsuccessful web request wrapper.
    """

    return {
        "status": 0,
        "message": message,
        "data": data
    }

class WebException(APIException):
    """
    Errors that are thrown that need to be displayed to the end user.
    """

    pass

class InternalException(APIException):
    """
    Exceptions thrown by the API constituting mild errors.
    """

    pass

class SevereInternalException(InternalException):
    """
    Exceptions thrown by the API constituting critical errors.
    """

    pass

def flat_multi(multidict):
    """
    Flattens any single element lists in a multidict.

    Args:
        multidict: multidict to be flattened.
    Returns:
        Partially flattened database.
    """

    flat = {}
    for key, values in multidict.items():
        flat[key] = values[0] if type(values) == list and len(values) == 1 \
                    else values
    return flat

def check(*callback_tuples):
    """
    Voluptuous wrapper function to raise our APIException

    Args:
        callback_tuples: a callback_tuple should contain (status, msg, callbacks)
    Returns:
        Returns a function callback for the Schema
    """

    def v(value):
        """
        Trys to validate the value with the given callbacks.

        Args:
            value: the item to validate
        Raises:
            APIException with the given error code and msg.
        Returns:
            The value if the validation callbacks are satisfied.
        """

        for msg, callbacks in callback_tuples:
            for callback in callbacks:
                try:
                    result = callback(value)
                    if not result and type(result) == bool:
                        raise Invalid()
                except Exception:
                    raise WebException(msg)
        return value
    return v

def validate(schema, data):
    """
    A wrapper around the call to voluptuous schema to raise the proper exception.

    Args:
        schema: The voluptuous Schema object
        data: The validation data for the schema object

    Raises:
        APIException with status 0 and the voluptuous error message
    """

    try:
        schema(data)
    except MultipleInvalid as error:
        raise APIException(0, None, error.msg)

def safe_fail(f, *args, **kwargs):
    """
    Safely calls a function that can raise an APIException.

    Args:
        f: function to call
        *args: positional arguments
        **kwargs: keyword arguments
    Returns:
        The function result or None if an exception was raised.
    """

    try:
        return f(*args, **kwargs)
    except APIException:
        return None
