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
        ("Invalid Event ID.", [int, Range(min=0, max=15)]),
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
name_map = [None] * 93

# Level 1
name_map[0] = "Tyrannosaurus Hex"

# Level 1 - Floor
name_map[1] = "The Valley of Fear"              # Left Closet
name_map[2] = "RoboPhoto"                       # Right bookshelf ("Locked CD")
name_map[3] = "No Comment"                      # Bottom of the table ("Just a CD")
name_map[4] = "Internet Inspection"             # The computer
name_map[5] = "Caesar"                          # Top of table
name_map[6] = "Common Vulnerability Exercise"   # Bedside table

# Level 2
name_map[7] = "Grep is Still Your Friend"                      # Upper right table ("Documents that need to be cracked")
name_map[8] = "Substitution"                       # Middle upper right ("hard drive is locked")
name_map[9] = "Javascrypt"                      # Officer needs your help
name_map[10] = "ZOR"                    # Officer needs your help
name_map[11] = "Basic ASM"                   # Officer needs your help
name_map[12] = "Spoof Proof"                            # Officer needs help "cracking this"
name_map[13] = "Pickle Jar"                     # Trying to get a log of father's phone calls
name_map[14] = "Easy Overflow"                  # Officer is stuck on a problem

# Level 3-1
name_map[15] = "Redacted"
name_map[16] = "Toaster Control"
name_map[17] = "Towers of Toast"

# Level 3-2
name_map[18] = "Delicious!"
name_map[19] = "Cyborg Secrets"
name_map[20] = "Intercepted Post"
name_map[21] = "Repeated XOR"
name_map[22] = "This is the Endian"

#---------------------------------
# Level 4
#---------------------------------

# Binary
name_map[23] = "Write Right"
name_map[24] = "ExecuteMe"
name_map[25] = "Best Shell"
name_map[26] = "ROP 1"
name_map[27] = "Overflow 1"
name_map[28] = "Overflow 2"
name_map[29] = "Nevernote"
name_map[30] = "Guess"
name_map[31] = "Format"
name_map[32] = "CrudeCrypt"

# Crypto
name_map[33] = None
name_map[34] = "Revenge of the Bleichenbacher"
name_map[35] = "Block"
name_map[36] = "Low Entropy"
name_map[37] = "Web Interception"
name_map[38] = "RSA"
name_map[39] = "ECC"
name_map[40] = None
name_map[41] = None
name_map[42] = None

# Forensics
name_map[43] = "Supercow"
name_map[44] = "PNG or Not?"
name_map[45] = "Snapcat"
name_map[46] = "Droid App"
name_map[47] = "SSH Backdoor"
name_map[48] = None
name_map[49] = None
name_map[50] = None
name_map[51] = None
name_map[52] = None

# Web
name_map[53] = "Injection 1"
name_map[54] = "Injection 2"
name_map[55] = "Injection 3"
name_map[56] = "Injection 4"
name_map[57] = "Massive Fail"
name_map[58] = "Potentially Hidden Password"
name_map[59] = "Make a Face"
name_map[60] = "secure_page_service"
name_map[61] = None
name_map[62] = None

# Misc
name_map[63] = "OBO"
name_map[64] = "No Overflow"
name_map[65] = "What The Flag"
name_map[66] = None
name_map[67] = None
name_map[68] = None
name_map[69] = None
name_map[70] = None
name_map[71] = None
name_map[72] = None

# Master
name_map[73] = "Baleful"
name_map[74] = "Hardcore ROP"
name_map[75] = "Steve's List"
name_map[76] = "RSA Mistakes"
name_map[77] = "Fancy Cache"
name_map[78] = None
name_map[79] = None
name_map[80] = None
name_map[81] = None
name_map[82] = None

# Reversing
name_map[83] = "Obfuscation"
name_map[84] = "Bit Puzzle"
name_map[85] = "Function Address"
name_map[86] = "Netsino"
name_map[87] = "Tick Tock"
name_map[88] = "Police Records"
name_map[89] = None
name_map[90] = None
name_map[91] = None
name_map[92] = None


etcid_map = None
pid_map = None

def gen_maps():
    global etcid_map, pid_map
    # grabs the pid of the problem and creates the mapping from index (etcid) to pid
    etcid_map = {}
    for i, name in enumerate(name_map):
        if name is not None:
            problem = api.problem.get_problem(name=name)
            if problem['category'] not in set(['Cryptography', 'Reverse Engineering', 'Web Exploitation', 'Binary Exploitation', 'Forensics', 'Miscellaneous', 'Master Challenge']):
                print("WARNING: %s uses invalid category %s" % (problem['name'], problem['category']))
            if problem is not None:
                etcid_map[i+1] = problem['pid']
            else:
                print("WARNING: No problem: %s" % name)
    pid_map = {v : k for k, v in etcid_map.items()}


def get_solved_indices():
    if pid_map is None:
        gen_maps()

    solved_problems = api.problem.get_solved_problems(api.user.get_team()['tid'])
    return WebSuccess(data=sorted([pid_map[p['pid']] for p in solved_problems if p['pid'] in pid_map.keys()]))


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


def get_problems():
    if etcid_map is None:
        gen_maps()
    useracct = api.user.get_user()
    unlocked_problems = [problem for problem in api.problem.get_unlocked_problems(useracct['tid']) if problem['pid'] in pid_map.keys()]
    solved_problems = [p['pid'] for p in api.problem.get_solved_problems(api.user.get_team()['tid'])]
    if 'viewed_problems' not in useracct:
        db = api.common.get_conn()
        db.users.update({'uid': useracct['uid']}, {'$set': {'viewed_problems': []}})
        none_viewed = True
    else:
        none_viewed = False
    for problem in unlocked_problems:
        if none_viewed:
            problem['viewed'] = False
        else:
            problem['viewed'] = pid_map[problem['pid']] in useracct['viewed_problems']
        problem['game_id'] = pid_map[problem['pid']]
        problem['solved'] = problem['pid'] in solved_problems
    return WebSuccess(data=unlocked_problems)


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

    if useracct['eventid'] <= eventid:
        db.users.update({'uid': useracct['uid']},
                        {'$set': {'avatar': avatar, 'eventid': eventid, 'level': level}})

    return WebSuccess("Update Successful")
