""" Module dealing with authentication to the api """

import bcrypt
import api

from flask import session
from voluptuous import Schema, Required, Length

from api.user import check
from api.annotations import log_action
from api.common import WebException, validate, safe_fail

log = api.logger.use(__name__)

debug_disable_general_login = False

user_login_schema = Schema({
    Required('username'): check(
        ("Usernames must be between 3 and 50 characters.", [str, Length(min=3, max=50)]),
    ),
    Required('password'): check(
        ("Passwords must be between 3 and 50 characters.", [str, Length(min=3, max=50)])
    )
})

def confirm_password(attempt, password_hash):
    """
    Verifies the password attempt

    Args:
        attempt: the password attempt
        password_hash: the real password pash
    """
    return bcrypt.hashpw(attempt, password_hash) == password_hash

@log_action
def login(username, password):
    """
    Authenticates a user.
    """

    # Read in submitted username and password
    validate(user_login_schema, {
        "username": username,
        "password": password
    })

    user = safe_fail(api.user.get_user, name=username)
    if user is None:
        raise WebException("Incorrect username.")

    if confirm_password(password, user['password_hash']):
        if debug_disable_general_login:
            if session.get('debugaccount', False):
                raise WebException("Correct credentials! But the game has not started yet...")
        if user['uid'] is not None:
            session['uid'] = user['uid']
            session.permanent = True
        else:
            raise WebException("Login Error")
    else:
        raise WebException("Incorrect Password")

@log_action
def logout():
    """ 
    Clears the session
    """
    
    session.clear()

def is_logged_in():
    """
    Check if the user is currently logged in.

    Returns:
        True if the user is logged in, false otherwise.
    """

    return 'uid' in session

def is_admin():
    """
    Check if the user is an admin. If the user as the 'admin' flag set in their session, they are an admin.

    Returns:
        True if the user is an admin, false otherwise.
    """

    return session.get('admin', False)

def get_uid():
    """
    Gets the user id from the session if it is logged in.

    Returns:
        The user id of the logged in user.
    """

    if is_logged_in():
        return session['uid']
    else:
        return None
