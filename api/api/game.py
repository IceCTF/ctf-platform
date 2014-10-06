__author__ = 'Jonathan Burket'

from api.annotations import *
from voluptuous import Required, Length, Schema, Range
from api.common import validate, check, WebException, WebSuccess, WebError

import api.problem
import api.user
import api.common

from api.app import app


game_state_schema = Schema({
    Required('avatar'): check(
        ("Invalid Avatar Value.", [int, Range(min=0, max=3)]),
    ),
    Required('eventid'): check(
        ("Invalid Event ID.", [int, Range(min=0, max=13)]),
    )
}, extra=True)


def get_category_statistics():
    db = api.common.get_conn()
    category_scores = {}
    for p in db.problems.find():
        if p['category'] in category_scores:
            category_scores[p['category']]['total'] += 1
        else:
            category_scores[p['category']] = {'solved': 0, 'total': 1}

    for p in api.problem.get_solved_problems(api.user.get_team()['tid']):
        category_scores[p['category']]['solved'] += 1

    return WebSuccess(data=category_scores)


# The index of the problem corresponds to its etc id
name_map = ["Failure to Boot", "Try Them All!", "Read the Manual", "Grep is Your Friend", "Spaceport Map",
            "Bitwise", "Byte Code", "CFG to C", "GETKey", "Robomunication", "First Contact",
            "Technician Challenge", "Yummy", "In Hex, No One Can Hear You Complain", "Spamcarver", "Core Decryption",
            "Chromatophoria", "Second Contact", "NAVSAT", "Dark Star", "Trivial", "Classic", "Harder Serial",
            "Python Eval 1", "Python Eval 2", "Python Eval 3", "Python Eval 4", "Python Eval 5", "avaJ", "Pretty Hard Programming",
            "Evergreen", "RSA", "Format 1", "Format 2", "ROP 1", "ROP 2", "ROP 3", "ROP 4", "Overflow 1", "Overflow 2",
            "Overflow 3", "Overflow 4", "Overflow 5", "Black Hole", "Broken CBC", "Injection", "Mildly Evil", 
            "Client-Side is the Best Side", "DDoS Detection", "PHP2", "PHP3", "PHP4", "moreevil", "hotcoffee", "Broken RSA" ]

etcid_map = None
pid_map = None

def gen_maps():
    global etcid_map, pid_map
    # grabs the pid of the problem and creates the mapping from index (etcid) to pid
    etcid_map = {i+1: api.problem.get_problem(name=name)['pid'] for i, name in enumerate(name_map)}
    pid_map = {v : k for k, v in etcid_map.items()}


def get_solved_indices():
    if pid_map is None:
        gen_maps()

    solved_problems = api.problem.get_solved_problems(api.user.get_team()['tid'])
    return WebSuccess(data=sorted([pid_map[p['pid']] for p in solved_problems]))


def get_game_problem(etcid):
    if etcid_map is None:
        gen_maps()

    useracct = api.user.get_user()
    try:
        pid = etcid_map[int(etcid)]
    except (IndexError, ValueError):
        raise WebException("Invalid Problem")

    p = api.problem.get_problem(pid=pid, tid=useracct['tid'])
    return WebSuccess(data=p)


def get_game_problem_status(etcid):
    if etcid_map is None:
        gen_maps()
    useracct = api.user.get_user()
    try:
        pid = int(etcid)
    except ValueError:
        return WebException("Invalid problem id")
    if 'viewed_problems' in useracct:
        if pid in useracct['viewed_problems']:
            return WebSuccess(data={'viewed': True})
    return WebSuccess(data={'viewed': False})


def set_game_problem_status(etcid, viewed):
    if etcid_map is None:
        gen_maps()

    useracct = api.user.get_user()
    uid = useracct['uid']
    db = api.common.get_conn()

    try:
        pid = int(etcid)
    except ValueError:
        return WebException("Invalid problem id")

    if 'viewed_problems' in useracct:
        viewed_problems = useracct['viewed_problems']
        if (pid not in viewed_problems) and viewed:
            viewed_problems += [pid]
            db.users.update({'uid': uid}, {'$set': {'viewed_problems': viewed_problems}})
        elif (pid in viewed_problems) and not viewed:
            viewed_problems.remove(pid)
            db.users.update({'uid': uid}, {'$set': {'viewed_problems': viewed_problems}})

    else:
        db.users.update({'uid': uid}, {'$set': {'viewed_problems': [pid]}})
    return WebSuccess()


def etcid_to_pid(etcid):
    if etcid_map is None:
        gen_maps()

    try:
        pid = etcid_map[int(etcid)]
        return WebSuccess(data=pid)
    except (IndexError, ValueError):
        raise WebException("Invalid Problem")


def get_state():
    useracct = api.user.get_user()
    return WebSuccess(data={
        'level': useracct['level'],
        'avatar': useracct['avatar'],
        'eventid': useracct['eventid']
    })


def update_state(avatar, eventid, level):
    db = api.common.get_conn()
    useracct = api.user.get_user()

    try:
        avatar = int(avatar)
        eventid = int(eventid)
    except ValueError:
        raise WebException("Invalid State Value Type")

    validate(game_state_schema, {
        "avatar": avatar,
        "eventid": eventid
    })

    db.users.update({'uid': useracct['uid']},
                    {'$set': {'avatar': avatar, 'eventid': eventid, 'level': level}})

    return WebSuccess("Update Successful")
