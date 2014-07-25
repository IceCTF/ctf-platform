#!/usr/bin/python3
import api
import time

api.cache.no_cache=True

while True:
    print("Calculating scoreboard..")
    f = api.scoreboard.get_all_team_scores
    api.cache.set(api.cache.get_mongo_key(f), f())
    print("Done!")
    time.sleep(60)
