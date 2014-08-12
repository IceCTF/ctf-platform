#!/usr/bin/python3

import api
import time, sys

def cache(f, *args, **kwargs):
    result = f(cache=False, *args, **kwargs)
    key = api.cache.get_mongo_key(f, *args, **kwargs)
    api.cache.set(key, result)

def run():
    cache(api.stats.get_all_team_scores)
    cache(api.stats.get_top_teams_score_progressions)
