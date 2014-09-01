""" Module for handling groups of teams """

import api

from voluptuous import Required, Length, Schema
from api.common import check, validate, safe_fail, WebException, InternalException, SevereInternalException

register_group_schema = Schema({
    Required("group-name"): check(
        ("Group name must be between 3 and 50 characters.", [str, Length(min=3, max=100)])
    )
}, extra=True)

join_group_schema = Schema({
    Required("group-name"): check(
        ("Group name must be between 3 and 50 characters.", [str, Length(min=3, max=100)]),
    )
}, extra=True)

leave_group_schema = Schema({
    Required("group-name"): check(
        ("Group name must be between 3 and 50 characters.", [str, Length(min=3, max=100)]),
    )
}, extra=True)

delete_group_schema = Schema({
    Required("group-name"): check(
        ("Group name must be between 3 and 50 characters.", [str, Length(min=3, max=100)]),
    )
}, extra=True)

def is_owner_of_group(gid):
    """
    Determine whether or not the current user is an owner of the group. gid must be specified.

    Args:
        gid: the group id
    Returns:
        Whether or not the user is a member of the group
    """

    group = get_group(gid=gid)

    if api.auth.is_logged_in():
        uid = api.user.get_user()["uid"]
    else:
        raise InternalException("cannot automatically retrieve tid if you aren't logged in.")

    return uid == group["owner"]

def is_member_of_group(gid=None, name=None, owner_uid=None, tid=None):
    """
    Determine whether or not a user is a member of the group. gid or name must be specified.

    Args:
        gid: the group id
        name: the group name
        owner_uid: uid of the group owner
        tid: the team id
    Returns:
        Whether or not the user is a member of the group
    """

    group = get_group(gid=gid, name=name, owner_uid=owner_uid)

    if tid is None:
        if api.auth.is_logged_in():
            tid = api.user.get_team()["tid"]
        else:
            raise InternalException("can not automatically retrieve tid if you aren't logged in.")

    return tid in group["members"]

def get_group(gid=None, name=None, owner_uid=None):
    """
    Retrieve a group based on its name or gid.

    Args:
        name: the name of the group
        gid: the gid of the group
        owner_uid: the uid of the group owner
    Returns:
        The group object.
    """

    db = api.common.get_conn()

    match = {}
    if name is not None and owner_uid is not None:
        match.update({"name": name})
        match.update({"owner": owner_uid})
    elif gid is not None:
        match.update({"gid": gid})
    else:
        raise InternalException("Group name and owner or gid must be specified to look it up.")

    group = db.groups.find_one(match, {"_id": 0})
    if group is None:
        raise InternalException("Could not find group!")

    return group

def get_member_information(gid):
    """
    Retrieves the team information for all teams in a group.

    Args:
        gid: the group id
    Returns:
        A list of team information
    """

    group = get_group(gid=gid)

    member_information = [api.team.get_team_information(tid) for tid in group["members"]]

    return member_information


def create_group(uid, group_name):
    """
    Inserts group into the db. Assumes everything is validated.

    Args:
        tid: The id of the team creating the group.
        group_name: The name of the group.
    Returns:
        The new group's gid.
    """

    db = api.common.get_conn()

    gid = api.common.token()

    db.groups.insert({
        "name": group_name,
        "owner": uid,
        "members": [],
        "gid": gid
    })

    return gid

def create_group_request(params, uid=None):
    """
    Creates a new group. Validates forms.
    All required arguments are assumed to be keys in params.

    Args:
        group-name: The name of the group

        Optional:
            uid: The uid of the user creating the group. If omitted,
            the uid will be grabbed from the logged in user.
    Returns:
        The new gid
    """

    if uid is None:
        uid = api.user.get_user()["uid"]

    validate(register_group_schema, params)

    if safe_fail(get_group, name=params["group-name"], owner_uid=uid) is not None:
        raise WebException("A group with that name already exists!")

    return create_group(uid, params["group-name"])

def join_group(tid, gid):
    """
    Adds a team to a group. Assumes everything is valid.

    Args:
        tid: the team id
        gid: the group id to join
    """

    db = api.common.get_conn()

    db.groups.update({'gid': gid}, {'$push': {'members': tid}})

def join_group_request(params, tid=None):
    """
    Tries to place a team into a group. Validates forms.
    All required arguments are assumed to be keys in params.

    Args:
        group-name: The name of the group to join.
        group-owner: The name of the owner of the group
        Optional:
            tid: If omitted,the tid will be grabbed from the logged in user.
    """

    owner_uid = api.user.get_user(name=params["group-owner"])["uid"]

    validate(join_group_schema, params)
    if safe_fail(get_group, name=params["group-name"], owner_uid=owner_uid) is None:
        raise WebException("No group exists with that name!")

    group = get_group(name=params["group-name"], owner_uid=owner_uid)

    if tid is None:
        tid = api.user.get_team()["tid"]

    if tid in group['members']:
        raise WebException("Your team is already a member of that group!")

    join_group(tid, group["gid"])

def leave_group(tid, gid):
    """
    Removes a team from a group

    Args:
        tid: the team id
        gid: the group id to leave
    """

    db = api.common.get_conn()

    db.groups.update({'gid': gid}, {'$pull': {'members': tid}})

def leave_group_request(params, tid=None):
    """
    Tries to remove a team from a group. Validates forms.
    All required arguments are assumed to be keys in params.

    Args:
        group-name: The name of the group to leave.
        group-owner: The owner of the group to leave.
        Optional:
            tid: If omitted,the tid will be grabbed from the logged in user.
    """

    validate(leave_group_schema, params)
    owner_uid = api.user.get_user(name=params["group-owner"])["uid"]
    group = get_group(name=params["group-name"], owner_uid=owner_uid)

    if tid is None:
        tid = api.user.get_team()["tid"]

    if tid not in group['members']:
        raise WebException("Your team is not a member of that group!")

    leave_group(tid, group["gid"])

def delete_group(gid):
    """
    Deletes a group

    Args:
        gid: the group id to delete
    """

    db = api.common.get_conn()

    db.groups.remove({'gid': gid})

def delete_group_request(params, uid=None):
    """
    Tries to delete a group. Validates forms.
    All required arguments are assumed to be keys in params.

    Args:
        group-name: The name of the group to join.
        Optional:
            uid: If omitted, the uid will be grabbed from the logged in user.
    """

    validate(delete_group_schema, params)

    if uid is None:
        uid = api.user.get_user()['uid']

    if safe_fail(get_group, name=params['group-name'], owner_uid=uid) is None:
        raise WebException("No group exists with that name!")

    if uid is None:
        uid = api.user.get_user()["uid"]

    group = get_group(name=params["group-name"], owner_uid=uid)

    delete_group(group['gid'])
