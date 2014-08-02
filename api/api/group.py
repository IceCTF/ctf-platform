""" Module for handling groups of teams """

import api

from voluptuous import Required, Length, Schema
from api.common import check, validate, safe_fail, WebException, InternalException, SevereInternalException

register_group_schema = Schema({
    Required("group-name"): check(
        ("Group name must be between 3 and 50 characters.", [str, Length(min=3, max=100)]),
        ("A group with that name already exists!", [
            lambda name: safe_fail(get_group, name=name) is None])
    )
})

join_group_schema = Schema({
    Required("group-name"): check(
        ("Group name must be between 3 and 50 characters.", [str, Length(min=3, max=100)]),
        ("No group exists with that name!", [
            lambda name: safe_fail(get_group, name=name) is not None]),
    )
})

leave_group_schema = Schema({
    Required("group-name"): check(
        ("Group name must be between 3 and 50 characters.", [str, Length(min=3, max=100)]),
        ("No group exists with that name!", [
            lambda name: safe_fail(get_group, name=name) is not None ]),
    )
})

delete_group_schema = Schema({
    Required("group-name"): check(
        ("Group name must be between 3 and 50 characters.", [str, Length(min=3, max=100)]),
        ("No group exists with that name!", [
            lambda name: safe_fail(get_group, name=name) is not None]),
    )
})

def get_group(gid=None, name=None):
    """
    Retrieve a group based on its name or gid.

    Args:
        name: the name of the group
        gid: the gid of the group
    Returns:
        The group object.
    """

    db = api.common.get_conn()

    match = {}
    if name is not None:
        match.update({"name": name})
    elif gid is not None:
        match.update({"gid": gid})
    else:
        raise InternalException("Group name or gid must be specified to look it up.")

    group = db.groups.find_one(match, {"_id": 0})
    if group is None:
        raise InternalException("Could not find group! You gave: " + str(match))

    return group

def create_group(tid, group_name):
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
        "owners": [tid],
        "members": [],
        "gid": gid
    })

    return gid

def create_group_request(params, tid=None):
    """
    Creates a new group. Validates forms.
    All required arguments are assumed to be keys in params.

    Args:
        group-name: The name of the group

        Optional:
            tid: The team id creating the group. If ommitted,
            the tid will be grabbed from the logged in user.
    Returns:
        The new gid
    """

    validate(register_group_schema, params)

    if tid is None:
        tid = api.user.get_team()["tid"]

    return create_group(tid, params["group-name"])

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

        Optional:
            tid: If omitted,the tid will be grabbed from the logged in user.
    """

    validate(join_group_schema, params)

    group = get_group(name=params["group-name"])

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
        name: the group name to leave
    """

    db = api.common.get_conn()

    db.groups.update({'gid': gid}, {'$pull': {'owners': tid}})
    db.groups.update({'gid': gid}, {'$pull': {'members': tid}})

def leave_group_request(params, tid=None):
    """
    Tries to remove a team from a group. Validates forms.
    All required arguments are assumed to be keys in params.

    Args:
        group-name: The name of the group to join.

        Optional:
            tid: If omitted,the tid will be grabbed from the logged in user.
    """

    validate(leave_group_schema, params)

    group = get_group(name=params["group-name"])

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

def delete_group_request(params, tid=None):
    """
    Tries to delete a group. Validates forms.
    All required arguments are assumed to be keys in params.

    Args:
        group-name: The name of the group to join.

        Optional:
            tid: If omitted,the tid will be grabbed from the logged in user.
    """

    validate(delete_group_schema, params)

    group = get_group(name=params["group-name"])

    if tid is None:
        tid = api.user.get_team()["tid"]

    if tid not in group['owners']:
        raise WebException("Your team is not an owner of that group!")

    delete_group(group['gid'])
