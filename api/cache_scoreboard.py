#!/usr/bin/python3
import api
import time

while True:
    f = api.stats.get_all_team_scores
    result = f(cache=False)
    key = api.cache.get_mongo_key(f)
    api.cache.set(key, result)
    time.sleep(60)
