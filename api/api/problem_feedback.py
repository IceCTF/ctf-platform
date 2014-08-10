""" Module for handling problem feedback """

import pymongo
import api

from datetime import datetime

from voluptuous import Schema, Required, Length
from api.common import validate, check, safe_fail, InternalException, SevereInternalException, WebException

feedback_schema = Schema({
    Required("metrics"): check(
        ("metrics must include difficulty, enjoyment, and educational-value", [
            lambda metrics: "difficulty" in metrics,
            lambda metrics: "enjoyment" in metrics,
            lambda metrics: "educational-value" in metrics
        ])
    ),
    "comment": check(
        ("The comment must be no more than 500 characters",[str, Length(max=500)])
    )
})

def get_problem_feedback(pid=None, tid=None, uid=None):
    """
    Retrieve feedback for a given problem, team, or user

    Args:
        pid: the problem id
        tid: the team id
        uid: the user id
    Returns:
        A list of problem feedback entries.
    """

    db = api.common.get_conn()
    match = {}

    if pid is not None:
        match.update({"pid": pid})
    if tid is not None:
        match.update({"tid": tid})
    if uid is not None:
        match.update({"uid": uid})

    return list(db.problem_feedback.find(match, {"_id": 0}))

def get_reviewed_pids(uid=None):
    """
    Gets the list of pids reviewed by the user

    Args:
        uid: the user id
    Returns:
        A list of pids
    """

    db = api.common.get_conn()

    if uid is None:
        uid = api.user.get_user()['uid']

    return [entry["pid"] for entry in get_problem_feedback(uid=uid)]

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
    solved = pid in api.problem.get_solved_pids(tid=team["tid"])

    validate(feedback_schema, feedback)

    db.problem_feedback.insert({
        "pid": pid,
        "uid": uid,
        "tid": team["tid"],
        "solved": solved,
        "timestamp": datetime.utcnow(),
        "feedback": feedback
    })
