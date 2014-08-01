""" Module for getting scoreboard information """

import api

from api.common import cache, APIException
from datetime import datetime

_get_problem_names = lambda problems: [problem['name'] for problem in problems]

end = datetime(2020, 5, 7, 3, 59, 59)

@api.cache.memoize()
def get_score(tid=None, uid=None):
    """
    Get the score for a user or team.

    Args:
        tid: The team id
        uid: The user id
    Returns:
        The users's or team's score
    """

    score = sum([problem['score'] for problem in api.problem.get_solved_problems(tid=tid, uid=uid)])

    return score

def get_group_scores(gid=None, name=None):
    """
    Get the group scores.

    Args:
        gid: The group id
        name: The group name
    Returns:
        A dictionary of tid:score mappings
    """

    members = [api.team.get_team(tid=tid) for tid in api.group.get_group(gid, name)['members']]

    result = []
    for team in members:
        result.append({
            "name": team['team_name'],
            "score": get_score(tid=team['tid'])
        })

    return sorted(result, key=lambda entry: entry['score'], reverse=True)

def get_group_score(gid=None, name=None):
    """
    Get the group score.

    Args:
        gid: The group id
        name: The group name
    Returns:
        The total score of the group
    """

    return sum([entry['score'] for entry in get_group_scores(gid, name)])

@api.cache.memoize()
def get_all_team_scores():
    """
    Gets the score for every team in the database.

    Returns:
        A list of dictionaries with name and score
    """

    teams = api.team.get_all_teams()

    result = []
    for team in teams:
        result.append({
            "name": team['team_name'],
            "score": get_score(tid=team['tid'])
        })

    return sorted(result, key=lambda entry: entry['score'], reverse=True)

def get_all_user_scores():
    """
    Gets the score for every user in the database.

    Returns:
        A list of dictionaries with name and score
    """

    users = api.user.get_all_users()

    result = []
    for user in users:
        result.append({
            "name": user['username'],
            "score": get_score(uid=user['uid'])
        })

    return sorted(result, key=lambda entry: entry['score'], reverse=True)

@api.cache.memoize(timeout=120, fast=True)
def problems_by_category():
    """
    Gets the list of all problems divided into categories

    Returns:
        A dictionary of category:[problem list]
    """

    result = {cat: _get_problem_names(api.problem.get_all_problems(category=cat))
                            for cat in api.problem.get_all_categories()}

    return result

def team_member_stats(tid):
    members = api.team.get_team_members(tid=tid)

    return {member['username']: _get_problem_names(api.problem.get_solved_problems(uid=member['uid']))}
