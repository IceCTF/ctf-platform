"""
API functions relating to user management and registration.
"""

import bcrypt, re, urllib, flask

import api

from api.common import check, validate, safe_fail
from api.common import WebException, InternalException
from api.annotations import log_action
from voluptuous import Required, Length, Schema

_check_email_format = lambda email: re.match(r"[A-Za-z0-9\._%+-]+@[A-Za-z0-9\.-]+\.[A-Za-z]{2,4}", email) is not None

user_schema = Schema({
    Required('email'): check(
        ("Email must be between 5 and 50 characters.", [str, Length(min=5, max=50)]),
        ("Your email does not look like an email address.", [_check_email_format])
    ),
    Required('firstname'): check(
        ("First Name must be between 1 and 50 characters.", [str, Length(min=1, max=50)])
    ),
    Required('lastname'): check(
        ("Last Name must be between 1 and 50 characters.", [str, Length(min=1, max=50)])
    ),
    Required('country'): check(
        ("Please select a country", [str, Length(min=2, max=2)])
    ),
    Required('username'): check(
        ("Usernames must be between 3 and 20 characters.", [str, Length(min=3, max=20)]),
        ("This username already exists.", [
            lambda name: safe_fail(get_user, name=name) is None])
    ),
    Required('password'):
        check(("Passwords must be between 3 and 20 characters.", [str, Length(min=3, max=20)])
    ),
    Required('background'):
        check(("You must provide your background!", [str, Length(min=3, max=20)])
    )
}, extra=True)

new_eligible_team_schema = Schema({
    Required('team-name-new'): check(
        ("The team name must be between 3 and 40 characters.", [str, Length(min=3, max=40)]),
        ("A team with that name already exists.", [
            lambda name: safe_fail(api.team.get_team, name=name) is None])
    ),
    Required('team-password-new'):
        check(("Team passphrase must be between 3 and 20 characters.", [str, Length(min=3, max=20)])),
    Required('team-adv-name-new'):
        check(("Adviser names should be between 3 and 50 characters.", [str, Length(min=3, max=50)])),
    Required('team-adv-email-new'): check(
        ("Adviser emails must be between 5 and 50 characters.", [str, Length(min=5, max=50)]),
        ("Your adviser email does not look like an email address.", [_check_email_format])
    ),
    Required('team-school-new'):
        check(("School names must be between 3 and 100 characters.", [str, Length(min=3, max=100)]))

}, extra=True)

new_team_schema = Schema({
    Required('team-name-new'): check(
        ("The team name must be between 3 and 40 characters.", [str, Length(min=3, max=40)]),
        ("A team with that name already exists.", [
            lambda name: safe_fail(api.team.get_team, name=name) is None])
    ),
    Required('team-password-new'):
        check(("Team passphrase must be between 3 and 20 characters.", [str, Length(min=3, max=20)])),

}, extra=True)

existing_team_schema = Schema({
    Required('team-name-existing'): check(
        ("Existing team names must be between 3 and 50 characters.", [str, Length(min=3, max=50)]),
        ("There is no existing team named that.", [
            lambda name: api.team.get_team(name=name) != None]),
        ("There are too many members on that team for you to join.", [
            lambda name: len(api.team.get_team_uids(name=name, show_disabled=False)) < api.team.max_team_users
        ])
    ),
    Required('team-password-existing'):
        check(("Team passwords must be between 3 and 50 characters.", [str, Length(min=3, max=50)]))
}, extra=True)

teacher_schema = Schema({
    Required('teacher-school'):
        check(("School names must be between 3 and 100 characters.", [str, Length(min=3, max=100)]))
}, extra=True)

def hash_password(password):
    """
    Hash plaintext password.

    Args:
        password: plaintext password
    Returns:
        Secure hash of password.
    """

    return bcrypt.hashpw(password, bcrypt.gensalt(8))

def get_team(uid=None):
    """
    Retrieve the the corresponding team to the user's uid.

    Args:
        uid: user's userid
    Returns:
        The user's team.
    """

    user = get_user(uid=uid)
    return api.team.get_team(tid=user["tid"])

def get_user(name=None, uid=None):
    """
    Retrieve a user based on a property. If the user is logged in,
    it will return that user object.

    Args:
        name: the user's username
        uid: the user's uid
    Returns:
        Returns the corresponding user object or None if it could not be found
    """

    db = api.common.get_conn()

    match = {}

    if uid is not None:
        match.update({'uid': uid})
    elif name is not None:
        match.update({'username': name})
    elif api.auth.is_logged_in():
        match.update({'uid': api.auth.get_uid()})
    else:
        raise InternalException("Uid or name must be specified for get_user")

    user = db.users.find_one(match)

    if user is None:
        raise InternalException("User does not exist")

    return user

def create_user(username, firstname, lastname, email, password_hash, tid, teacher=False,
                background="undefined", country="undefined", receive_ctf_emails=False):
    """
    This inserts a user directly into the database. It assumes all data is valid.

    Args:
        username: user's username
        firstname: user's first name
        lastname: user's last name
        email: user's email
        password_hash: a hash of the user's password
        tid: the team id to join
        teacher: whether this account is a teacher
    Returns:
        Returns the uid of the newly created user
    """

    db = api.common.get_conn()
    uid = api.common.token()

    if safe_fail(get_user, name=username) is not None:
        raise InternalException("User already exists!")

    user = {
        'uid': uid,
        'firstname': firstname,
        'lastname': lastname,
        'username': username,
        'email': email,
        'password_hash': password_hash,
        'tid': tid,
        'teacher': teacher,
        'avatar': 3,
        'eventid': 0,
        'level': 'Not Started',
        'background': background,
        'country': country,
        'receive_ctf_emails': receive_ctf_emails
    }

    db.users.insert(user)

    return uid

def get_all_users(show_teachers=False):
    """
    Finds all the users in the database

    Args:
        show_teachers: whether or not to include teachers in the response
    Returns:
        Returns the uid, username, and email of all users.
    """

    db = api.common.get_conn()

    match = {}
    projection = {"uid": 1, "username": 1, "email": 1, "tid": 1}

    if not show_teachers:
        match.update({"teacher": False})
        projection.update({"teacher": 1})

    return list(db.users.find(match, projection))

def _validate_captcha(data):
    """
    Validates a captcha with google's reCAPTCHA.

    Args:
        data: the posted form data
    """

    post_data = urllib.parse.urlencode({
        "privatekey": api.config.reCAPTCHA_private_key,
        "remoteip": flask.request.remote_addr,
        "challenge": data["recaptcha_challenge_field"],
        "response": data["recaptcha_response_field"]
    }).encode("utf-8")

    request = urllib.request.Request(api.config.captcha_url, post_data)
    response = urllib.request.urlopen(request).read().decode("utf-8")
    return response.split("\n")[0].lower() == "true"

@log_action
def create_user_request(params):
    """
    Registers a new user and creates/joins a team. Validates all fields.
    Assume arguments to be specified in a dict.

    Args:
        username: user's username
        password: user's password
        firstname: user's first name
        lastname: user's first name
        email: user's email
        create-new-teacher:
            boolean "true" indicating whether or not the user is a teacher
        create-new-team:
            boolean "true" indicating whether or not the user is creating a new team or
            joining an already existing team.

        team-name-existing: Name of existing team to join.
        team-password-existing: Password of existing team to join.

        team-name-new: Name of new team.
        team-adv-name-new: Name of adviser.
        team-adv-email-new: Adviser's email address.
        team-school-new: Name of the team's school.
        team-password-new: Password to join team.

    """

    validate(user_schema, params)

    if api.config.enable_captcha and not _validate_captcha(params):
        raise WebException("Incorrect captcha!")

    #Why are these strings? :o
    if params.get("create-new-teacher", "false") == "true":
        if not api.config.enable_teachers:
            raise WebException("Could not create account")

        validate(teacher_schema, params)

        tid = api.team.create_team({
            "eligible": False,
            "school": params["teacher-school"],
            "team_name": "TEACHER-" + api.common.token()
        })

        return create_user(
            params["username"],
            params["firstname"],
            params["lastname"],
            params["email"],
            hash_password(params["password"]),
            tid,
            teacher=True,
            background=params["background"],
            country=params["country"],
            receive_ctf_emails=params["ctf-emails"]
        )

    elif params.get("create-new-team", "false") == "true":

        # JB: Remove this for public release
        eligible = params['country'] == "US" and params['background'] in ['student_el', 'student_ms', 'student_hs', 'student_home']

        if eligible:
            validate(new_eligible_team_schema, params)
        else:
            validate(new_team_schema, params)


        team_params = {
            "team_name": params["team-name-new"],
            "adviser_name": params["team-adv-name-new"],
            "adviser_email": params["team-adv-email-new"],
            "school": params["team-school-new"],
            "password": params["team-password-new"],
            "eligible": eligible
        }

        tid = api.team.create_team(team_params)

        if tid is None:
            raise InternalException("Failed to create new team")
        team = api.team.get_team(tid=tid)
    else:
        validate(existing_team_schema, params)

        team = api.team.get_team(name=params["team-name-existing"])

        if team['password'] != params['team-password-existing']:
            raise WebException("Your team passphrase is incorrect.")

    # Create new user
    uid = create_user(
        params["username"],
        params["firstname"],
        params["lastname"],
        params["email"],
        hash_password(params["password"]),
        team["tid"],
        background=params["background"],
        country=params["country"],
        receive_ctf_emails=params["ctf-emails"]
    )

    if uid is None:
        raise InternalException("There was an error during registration.")

    return uid

def is_teacher(uid=None):
    """
    Determines if a user is a teacher.

    Args:
        uid: user's uid
    Returns:
        True if the user is a teacher, False otherwise
    """

    user = get_user(uid=uid)
    return user.get('teacher', False)

def set_password_reset_token(uid, token):
    """
    Sets the password reset token for the user in mongo

    Args:
        uid: the user id
        token: the token to set
    """

    db = api.common.get_conn()
    db.users.update({'uid': uid}, {'$set': {'password_reset_token': token}})

def delete_password_reset_token(uid):
    """
    Removes the password reset token for the user in mongo

    Args:
        uid: the user id
    """

    db = api.common.get_conn()
    db.users.update({'uid': uid}, {'$unset': {'password_reset_token': ''}})

def find_user_by_reset_token(token):
    """
    Searches the database for a team with the given password reset token
    """

    db = api.common.get_conn()
    user = db.users.find_one({'password_reset_token': token})

    if user is None:
        raise WebException("That is not a valid password reset token!")

    return user

def update_password(uid, password):
    """
    Updates an account's password.

    Args:
        uid: user's uid.
        password: the new user password.
    """

    db = api.common.get_conn()
    db.users.update({'uid': uid}, {'$set': {'password_hash': hash_password(password)}})

def disable_account(uid):
    """
    Disables a user account. They will no longer be able to login and do not count
    towards a team's maximum size limit.

    Args:
        uid: user's uid
    """

    db = api.common.get_conn()
    db.users.update({"uid": uid}, {"$set": {"disabled": True}})

@log_action
def disable_account_request(params, uid=None, check_current=False):
    """
    Disable user account so they can't login or consume space on a team.
    Assumes args are keys in params.

    Args:
        uid: uid to reset
        check_current: whether to ensure that current-password is correct
        params:
            current-password: the users current password
    """

    user = get_user(uid=uid)

    if check_current and not api.auth.confirm_password(params["current-password"], user['password_hash']):
        raise WebException("Your current password is incorrect.")
    disable_account(user['uid'])

    api.auth.logout()
