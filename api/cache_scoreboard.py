#!/usr/bin/python3
import api
import time

# kind of a hacky, but it works
api.cache.no_cache=True

while True:
    f = api.scoreboard.get_all_team_scores
    result = f()
    api.cache.invalidate_memoization(f, {})
    api.cache.set(api.cache.get_mongo_key(f), result)
    time.sleep(60)
