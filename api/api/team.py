"""
API functions relating to team management.
"""

import api

from api.common import safe_fail, WebException, InternalException, SevereInternalException

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

def get_groups(tid=None, uid=None):
    """
    Get the group membership for a team.

    Args:
        tid: The team id
        uid: The user id
    Returns:
        List of group objects the team is a member of.
    """

    tid = get_team(tid=tid)["tid"]
    if uid is None:
        uid = api.user.get_user()["uid"]

    db = api.common.get_conn()

    groups = []

    for group in list(db.groups.find({'owner': uid}, {'name': 1, 'gid': 1, 'owner': 1, 'members': 1})):
        owner = api.user.get_user(uid=group['owner'])['username']
        groups.append({'name': group['name'],
                       'gid': group['gid'],
                       'members': group['members'],
                       'owner': owner,
                       'score': api.stats.get_group_average_score(gid=group['gid'])})

    for group in list(db.groups.find({'members': tid}, {'name': 1, 'gid': 1, 'owner': 1})):
        owner = api.user.get_user(uid=group['owner'])['username']
        groups.append({'name': group['name'],
                       'gid': group['gid'],
                       'owner': owner,
                       'score': api.stats.get_group_average_score(gid=group['gid'])})
    return groups

def create_team(params):
    """
    Directly inserts team into the database. Assumes all fields have been validated.

    Args:
        team_name: Name of the team
        school: Name of the school
        password: Team's password
        eligible: the teams eligibility
    Returns:
        The newly created team id.
    """

    db = api.common.get_conn()

    if not shell_accounts_available() and api.config.enable_shell:
        raise SevereInternalException("There are no shell accounts available.")

    params['tid'] = api.common.token()
    params['size'] = 0

    db.teams.insert(params)

    if api.config.enable_shell:
        assign_shell_account(params["tid"])

    return params['tid']

def get_team_members(tid=None, name=None, show_disabled=True):
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

    users = list(db.users.find({"tid": tid}, {"_id": 0, "uid": 1, "username": 1, "disabled": 1}))
    return [user for user in users if show_disabled or not user.get("disabled", False)]

def get_team_uids(tid=None, name=None, show_disabled=True):
    """
    Gets the list of uids that belong to a team

    Args:
        tid: the team id
        name: the team name
    Returns:
        A list of uids
    """

    return [user['uid'] for user in get_team_members(tid=tid, name=name, show_disabled=show_disabled)]

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
    team_info["members"] = [member["username"] for member in get_team_members(tid=tid, show_disabled=False)]
    team_info["competition_active"] = api.utilities.check_competition_active()
    team_info["max_team_size"] = max_team_users

    if api.config.enable_achievements:
        team_info["achievements"] = api.achievement.get_earned_achievements(tid=tid)

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

def shell_accounts_available():
    """
    Determines whether or not shell accounts are available.

    Returns:
        Whether or not accounts are available.
    """

    db = api.common.get_conn()

    return db.ssh.find({"tid": {"$exists": False}}).count() > 0

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

def assign_shell_account(tid=None):
    """
    Assigns a webshell account for the team.

    Args:
        tid: the team id
    """

    db = api.common.get_conn()

    tid = get_team(tid=tid)["tid"]

    if db.ssh.find({"tid": tid}).count() > 0:
        raise InternalException("Team {} was already assigned a shell account.".format(tid))

    if not shell_accounts_available():
        raise InternalException("There are no available shell accounts.")

    db.ssh.update({"tid": {"$exists": False}}, {"$set": {"tid": tid}}, multi=False)


def determine_eligibility(tid=None):
    db = api.common.get_conn()
    members = [x for x in db.users.find({"tid": tid}) if 'disabled' not in x or not x['disabled']]
    team = api.team.get_team(tid=tid)
    if 'disqualified' in team and team['disqualified']:
        eligible = False
        justification = ["Team has been disqualified"]
    elif len(members) == 0:
        eligible = False
        justification = ["Team has no members"]
    else:
        eligible = True
        justification = []
        for member in members:
            if member['background'] not in set(['student_hs', 'student_ms', 'student_el', 'student_home']):
                eligible = False
                justification.append("User %s is not a middle or high school student" % member['username'])
            if member['country'] != "US":
                eligible = False
                justification.append("User %s is not from the United States" % member['username'])
    db.teams.update({'tid': tid}, {'$set': {'eligible': eligible, 'justification': justification}})
    return eligible



def recalculate_all_eligibility():
    for team in get_all_teams(show_ineligible=True):
        determine_eligibility(team['tid'])
