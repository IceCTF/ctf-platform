import api

from api.common import safe_fail, WebException, InternalException, SevereInternalException


def get_team_tshirt_info(tid=None, name=None, show_disabled=False):
    db = api.common.get_conn()
    team = api.team.get_team(name=name, tid=tid)
    users = list(db.users.find({"tid": team['tid']}, {"_id": 0, "uid": 1, "username": 1,
                                                      "disabled": 1, "shirtsize": 1, "shirttype": 1}))
    result = {'team_name': team['team_name'],
              'adviser_name': team['adviser_name'],
              'adviser_email': team['adviser_email'],
              'address': team.get('address', ""),
              'tshirt_winner': team.get('tshirt_winner', ""),
              'members': [user for user in users if show_disabled or not user.get("disabled", False)]}
    return result


def set_tshirt_info(users, address):
    team = api.team.get_team()
    team_uids = set([user['uid'] for user in api.team.get_team_members(tid=team['tid'], show_disabled=False)])
    db = api.common.get_conn()
    for uid, values in users.items():
        if uid not in team_uids:
            raise WebException("Status set for invalid user")
        db.users.update({'uid': uid}, {'$set': {'shirtsize': values['size'], 'shirttype': values['gender']}})
    db.teams.update({'tid': team['tid']}, {'$set': {'address': address}})