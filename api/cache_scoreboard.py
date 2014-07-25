#!/usr/bin/python3
import api
import time

api.cache.no_cache=True

while True:
    print("Calculating scoreboard..")
    f = api.scoreboard.get_all_team_scores
    result = f()
    api.cache.invalidate_memoization(f, {})
    api.cache.set(api.cache.get_mongo_key(f), result)
    print("Done!")
    time.sleep(60)
