""" Module for handling problem feedback """

import pymongo
import api

from api.common import validate, check, safe_fail, InternalException, SevereInternalException, WebException

def get_problem_feedback(pid, tid=None, uid=None):
    """
    Retrieve feedback for a given problem. pid is required.

    Args:
        pid: the problem id
        tid: the team id
        uid: the user id
    Returns:
        A list of problem feedback entries.
    """

    db = api.common.get_conn()
    match = {"pid": pid}

    if tid:
        match.update({"tid": tid})
    if uid:
        match.update({"uid": uid})

    return list(db.problem_feedback.find(match, {"_id": 0}))

def add_problem_feedback(pid, uid, feedback):
    """
    Add user problem feedback to the database.

    Args:
        pid: the problem id
        uid: the user id
        feedback: the problem feedback.
    """

    db = api.common.get_conn()

    #Make sure the problem actually exists.
    api.problem.get_problem(pid=pid)
    team = api.user.get_team(uid=uid)
    solved = pid in api.problems.get_solved_pids(tid=team["tid"])

    db.problem_feedback.insert({
        "pid": pid,
        "uid": uid,
        "tid": team["tid"],
        "feedback": feedback
    })
