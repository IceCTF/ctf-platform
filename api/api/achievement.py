""" Module for interacting with the achievements """

import imp
import pymongo

import api

from os.path import join
from voluptuous import Schema, Required, Range
from api.common import check, InternalException, SevereInternalException, validate, safe_fail

processor_base_path = "./processors"

achievement_schema = Schema({
    Required("name"): check(
        ("The achievement's display name must be a string.", [str])),
    Required("score"): check(
        ("Score must be a positive integer.", [int, Range(min=0)])),
    Required("event"): check(
        ("Type must be a string.", [str])),
    Required("description"): check(
        ("The description must be a string.", [str])),
    Required("processor"): check(
        ("The processor path must be a string.", [str])),
    Required("hidden"): check(
        ("An achievement's hidden state is either True or False.", [
            lambda hidden: type(hidden) == bool])),
    Required("image"): check(
        ("An achievement's image path must be a string.", [str])),
    "disabled": check(
        ("An achievement's disabled state is either True or False.", [
            lambda disabled: type(disabled) == bool])),
    "aid": check(
        ("You should not specify a aid for an achievement.", [lambda _: False])),
    "_id": check(
        ("Your achievements should not already have _ids.", [lambda id: False]))
})

def get_all_events(show_disabled=False):
    """
    Gets the set of distinct achievement events.

    Args:
        show_disabled: Whether to include events that are only on disabled achievements
    Returns:
        The set of distinct achievement events.
    """

    db = api.common.get_conn()

    match = {}
    if not show_disabled:
        match.update({"disabled": False})

    return db.achievemets.find(match).distinct("event")

def get_achievement(aid=None, name=None, show_disabled=False):
    """
    Gets a single achievement

    Args:
        aid: the achievement id
        name: the name of the achievement
        show_disabled: Boolean indicating whether or not to show disabled achievements.
    """

    db = api.common.get_conn()

    match = {}

    if aid is not None:
        match.update({'aid': aid})
    elif name is not None:
        match.update({'name': name})
    else:
        raise InternalException("Must supply aid or display name")

    if not show_disabled:
        match.update({"disabled": False})

    db = api.common.get_conn()
    achievement = db.achievements.find_one(match, {"_id":0})

    if achievement is None:
        raise SevereInternalException("Could not find achievement! You gave " + str(match))

    return achievement

def get_all_achievements(event=None, show_disabled=False):
    """
    Gets all of the achievements in the database.

    Args:
        event: Optional parameter to restrict which achievements are returned
        show_disabled: Boolean indicating whether or not to show disabled achievements.
    Returns:
        List of achievements from the database
    """

    db = api.common.get_conn()

    match = {}
    if event is not None:
        match.update({'event': event})

    if not show_disabled:
        match.update({'disabled': False})

    return list(db.achievements.find(match, {"_id":0}).sort('score', pymongo.ASCENDING))

def get_earned_achievement_entries(tid=None, uid=None, aid=None):
    """
    Gets the solved achievements for a given team or user.

    Args:
        tid: The team id
        event: Optional parameter to restrict which achievements are returned
    Returns:
        List of solved achievements
    """

    db = api.common.get_conn()

    match = {}

    if uid is not None:
        match.update({"uid": uid})
    elif tid is not None:
        match.update({"tid": tid})

    if aid is not None:
        match.update({"aid": aid})

    return list(db.achievements.find(match, {"_id":0}))

def get_earned_aids(tid=None, uid=None, aid=None):
    """
    Gets the solved aids for a given team or user.

    Args:
        tid: The team id
        event: Optional parameter to restrict which achievements are returned
    Returns:
        List of solved achievement ids
    """

    return [a["aid"] for a in get_earned_achievement_entries(tid=tid, uid=uid, aid=None)]

def get_earned_achievements(tid=None, uid=None):
    """
    Gets the solved achievements for a given team or user.

    Args:
        tid: The team id
        tid: The user id
    Returns:
        List of solved achievement dictionaries
    """

    return [get_achievement(aid=aid) for aid in get_earned_achievement_entries(tid=tid, uid=uid)]

def reevaluate_earned_achievements(aid=None):
    """
    In the case of the achievement or processor being updated, this will reevaluate earned achievements for an achievement.

    Args:
        aid: the aid of the achievement to be reevaluated.
    """

def reevaluate_all_earned_acheivements():
    """
    In the case of the achievement or processor being updated, this will reevaluate all earned achievements.
    """

def set_achievement_disabled(aid, disabled):
    """
    Updates a achievement's availability.

    Args:
        aid: the achievement's aid
        disabled: whether or not the achievement should be disabled.
    Returns:
        The updated achievement object.
    """

def get_processor(aid):
    """
    Returns the processor module for a given achievement.

    Args:
        aid: the achievement id
    Returns:
        The processor module
    """

    try:
        path = get_achievement(aid=aid, show_disabled=True)["grader"]
        return imp.load_source(path[:-3], join(achievement_base_path, path))
    except FileNotFoundError:
        raise InternalException("Achievement processor is offline.")

def process_achievement(aid, uid=None):
    """
    Determines whether or not an achievement has been earned.

    Args:
        aid: the achievement id
        uid: the user id
    """

    if uid is None:
        uid = api.user.get_user()["uid"]

    tid = api.user.get_user(uid=uid)["tid"]

    achievement = get_achievement(aid=aid, show_disabled=True)
    processor = get_processor(aid)

    return processor.process(api, tid, uid)

def process_achievements(*events):
    """
    Annotations for processing achievements of a given event type.
    """

    def clear(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            db = api.common.get_conn()
            result = f(*args, **kwargs)

            user = api.user.get_user()
            tid = user["tid"]
            uid = user["uid"]

            for event in events:

                eligible_achievements = [
                    achievement for achievement in get_all_achievements(event=event) \
                        if achievement not in get_earned_achievements(tid=tid)]

                for achievement in eligible_achievements:
                    aid = achievement["aid"]

                        insert_earned_achievement(aid, tid, uid)

            return result
        return wrapper
    return clear

def insert_achievement(achievement):
    """
    Inserts an achievement object into the database.

    Args:
        achievement: the achievement object loaded from json.
    Returns:
        The achievment's aid.
    """

    db = api.common.get_conn()
    validate(achievement_schema, achievement)

    achievement["disabled"] = achievement.get("disabled", False)

    achievement["aid"] = api.common.hash(achievement["name"])

    if safe_fail(get_achievement, aid=achievement["aid"]) is not None:
        raise WebException("achievement with identical aid already exists.")

    if safe_fail(get_achievement, name=achievement["name"]) is not None:
        raise WebException("achievement with identical name already exists.")

    db.achievements.insert(achievement)
    api.cache.fast_cache.clear()

    return achievement["aid"]
