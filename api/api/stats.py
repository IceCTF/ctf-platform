""" Module for getting competition statistics"""

import api
import datetime

_get_problem_names = lambda problems: [problem['name'] for problem in problems]
top_teams = 10

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


def get_team_review_count(tid=None, uid=None):
    if uid is not None:
        return len(api.problem_feedback.get_reviewed_pids(uid=uid))
    elif tid is not None:
        count = 0
        for member in api.team.get_team_members(tid=tid):
            count += len(api.problem_feedback.get_reviewed_pids(uid=member['uid']))
        return count


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

def get_group_average_score(gid=None, name=None):
    """
    Get the average score of teams in a group.

    Args:
        gid: The group id
        name: The group name
    Returns:
        The total score of the group
    """

    group_scores = get_group_scores(gid=gid, name=name)
    total_score = sum([entry['score'] for entry in group_scores])
    return int(total_score / len(group_scores)) if len(group_scores) > 0 else 0

# Stored by the cache_stats daemon
@api.cache.memoize()
def get_all_team_scores():
    """
    Gets the score for every team in the database.

    Returns:
        A list of dictionaries with name and score
    """

    teams = api.team.get_all_teams()
    db = api.api.common.get_conn()

    result = []
    for team in teams:
        if db.submissions.find({'tid': team['tid'], 'eligible': True}).count() > 0:
            lastsubmit = db.submissions.find({'tid': team['tid'], 'eligible': True}).sort('timestamp')[0]['timestamp']
        else:
            lastsubmit = datetime.datetime.now()
        score = get_score(tid=team['tid'])
        if score > 0:
            result.append({
                "name": team['team_name'],
                "tid": team['tid'],
                "school": team["school"],
                "score": score,
                "lastsubmit": lastsubmit
            })

    time_ordered = sorted(result, key=lambda entry: entry['lastsubmit'], reverse=True)
    return sorted(time_ordered, key=lambda entry: entry['score'], reverse=True)


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
def get_problems_by_category():
    """
    Gets the list of all problems divided into categories

    Returns:
        A dictionary of category:[problem list]
    """

    result = {cat: _get_problem_names(api.problem.get_all_problems(category=cat))
                            for cat in api.problem.get_all_categories()}

    return result


@api.cache.memoize(timeout=120, fast=True)
def get_pids_by_category():
    result = {cat: [x['pid'] for x in api.problem.get_all_problems(category=cat)]
              for cat in api.problem.get_all_categories()}
    return result


@api.cache.memoize(timeout=120, fast=True)
def get_pid_categories():
    pid_map = {}
    for cat in api.problem.get_all_categories():
        for p in api.problem.get_all_problems(category=cat):
            pid_map[p['pid']] = cat
    return pid_map


def get_team_member_stats(tid):
    """
    Gets the solved problems for each member of a given team.

    Args:
        tid: the team id

    Returns:
        A dict of username:[problem list]
    """

    members = api.team.get_team_members(tid=tid)

    return {member['username']: _get_problem_names(api.problem.get_solved_problems(uid=member['uid'])) for member in members}

@api.cache.memoize()
def get_score_progression(tid=None, uid=None, category=None):
    """
    Finds the score and time after each correct submission of a team or user.
    NOTE: this is slower than get_score. Do not use this for getting current score.

    Args:
        tid: the tid of the user
        uid: the uid of the user
        category: category filter
    Returns:
        A list of dictionaries containing score and time
    """

    correct_submissions = api.problem.get_submissions(uid=uid, tid=tid, category=category, correctness=True)

    result = []
    score = 0

    for submission in sorted(correct_submissions, key=lambda sub: sub["timestamp"]):
        score += api.problem.get_problem(pid=submission["pid"])["score"]
        result.append({
            "score": score,
            "time": int(submission["timestamp"].timestamp())
        })

    return result

def get_top_teams():
    """
    Finds the top teams

    Returns:
        The top teams and their scores
    """

    all_teams = api.stats.get_all_team_scores()
    return all_teams if len(all_teams) < top_teams else all_teams[:top_teams]

# Stored by the cache_stats daemon
@api.cache.memoize()
def get_top_teams_score_progressions():
    """
    Gets the score_progressions for the top teams

    Returns:
        The top teams and their score progressions.
        A dict of {team_name: score_progression}
    """

    return [{
        "name": team["name"],
        "score_progression": get_score_progression(tid=team["tid"]),
    } for team in get_top_teams()]
