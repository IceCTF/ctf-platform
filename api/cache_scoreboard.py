#!/usr/bin/python3

import api
import time

def cache_team_scores():
    """
    A hacky looking way to evaluate and cache the call to get_all_team_scores.
    """

    f = api.stats.get_all_team_scores
    result = f(cache=False)
    key = api.cache.get_mongo_key(f)
    api.cache.set(key, result)

while True:
    cache_team_scores()
    time.sleep(60)
