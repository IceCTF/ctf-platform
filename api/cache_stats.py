#!/usr/bin/python3

import api
import time, sys

INTERVAL = int(sys.argv[1]) if len(sys.argv) > 1 else 60

def cache(f, *args, **kwargs):
    result = f(cache=False, *args, **kwargs)
    key = api.cache.get_mongo_key(f, *args, **kwargs)
    api.cache.set(key, result)

while True:
    cache(api.stats.get_all_team_scores)
    cache(api.stats.get_top_teams_score_progressions)
    time.sleep(INTERVAL)
