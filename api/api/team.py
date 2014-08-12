"""
API functions relating to team management.
"""

import api

from api.common import safe_fail, WebException, InternalException

max_team_users = 5

def get_team(tid=None, name=None):
    """
    Retrieve a team based on a property (tid, name, etc.).

    Args:
        tid: team id
        name: team name
    Returns:
        Returns the corresponding team object or None if it could not be found
    """

    db = api.api.common.get_conn()

    match = {}
    if tid is not None:
        match.update({'tid': tid})
    elif name is not None:
        match.update({'team_name': name})
    elif api.auth.is_logged_in():
        match.update({"tid": api.user.get_user()["tid"]})
    else:
        raise InternalException("Must supply tid or team name to get_team")

    team = db.teams.find_one(match, {"_id": 0})

    if team is None:
        raise InternalException("Team does not exist.")

    return team

def get_groups(tid=None):
    """
    Get the group membership for a team.

    Args:
        tid: The team id
    Returns:
        List of group objects the team is a member of.
    """

    tid = get_team(tid=tid)["tid"]

    db = api.common.get_conn()

    groups = []

    for group in list(db.groups.find({'owners': tid}, {'name': 1, 'gid': 1, 'owners': 1, 'members': 1})):
        groups.append({'name': group['name'],
                       'gid': group['gid'],
                       'members': group['members'],
                       'score': api.stats.get_group_average_score(gid=group['gid'])})

    for group in list(db.groups.find({'members': tid}, {'name': 1, 'gid': 1})):
        groups.append({'name': group['name'],
                       'gid': group['gid'],
                       'score': api.stats.get_group_average_score(gid=group['gid'])})
    return groups

def create_team(params):
    """
    Directly inserts team into the database. Assumes all fields have been validated.

    Args:
        team_name: Name of the team
        adviser_name: Full name of the team's adviser
        adviser_email: Adviser's email address
        school: Name of the school
        password: Team's password
        eligible: the teams eligibility
    Returns:
        The newly created team id.
    """

    db = api.common.get_conn()

    params['tid'] = api.common.token()

    db.teams.insert(params)

    return params['tid']

def get_team_members(tid=None, name=None):
    """
    Retrieves the members on a team.

    Args:
        tid: the team id to query
        name: the team name to query
    Returns:
        A list of the team's members.
    """

    db = api.common.get_conn()

    tid = get_team(name=name, tid=tid)["tid"]

    return list(db.users.find({"tid": tid}, {"_id": 0, "uid": 1, "username": 1}))

def get_team_uids(tid=None, name=None):
    """
    Gets the list of uids that belong to a team

    Args:
        tid: the team id
        name: the team name
    Returns:
        A list of uids
    """

    return [team['uid'] for team in get_team_members(tid=tid, name=name)]

def get_team_information(tid=None):
    """
    Retrieves the information of a team.

    Args:
        tid: the team id
    Returns:
        A dict of team information.
            team_name
            members
    """

    team_info = get_team(tid=tid)

    if tid is None:
       tid = team_info["tid"] 

    team_info["score"] = api.stats.get_score(tid=tid)
    team_info["members"] = [member["username"] for member in get_team_members(tid=tid)]

    return team_info

def get_all_teams(show_ineligible=False):
    """
    Retrieves all teams.

    Returns:
        A list of all of the teams.
    """

    match = {}

    if not show_ineligible:
        match.update({"eligible": True})

    db = api.common.get_conn()
    return list(db.teams.find(match, {"_id": 0}))

def get_shell_account(tid=None):
    """
    Retrieves a team's shell account credentials.

    Args:
        tid: the team id. If no tid is specified, will try to get the active user's tid.
    Returns:
        The shell object. {username, password, hostname, port}
    """

    db = api.common.get_conn()

    tid = get_team(tid)["tid"]

    shell_account = db.ssh.find_one({"tid": tid}, {"_id": 0, "tid": 0})

    if shell_account is None:
        raise InternalException("Team {} was not assigned a shell account.".format(tid))

    return shell_account

def assign_shell_account(tid):
    """
    Assigns a webshell account for the team.

    Args:
        tid: the team id
    """

    db = api.common.get_conn()

    tid = get_team(tid=tid)["tid"]

    if db.ssh.find({"tid": tid}).count() > 0:
        raise InternalException("Team {} was already assigned a shell account.")

    if db.ssh.find({"tid": {"$exists": False}}).count() == 0:
        raise InternalException("There are no available shell accounts.")

    db.ssh.update({"tid": {"$exists": False}}, {"$set": {"tid": tid}}, multi=False)
