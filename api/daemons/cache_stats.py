#!/usr/bin/python3

import api
import time, sys

def cache(f, *args, **kwargs):
    result = f(cache=False, *args, **kwargs)
    key = api.cache.get_mongo_key(f, *args, **kwargs)
    api.cache.set(key, result)

def run():
    print("Caching the public scoreboard entries...")
    cache(api.stats.get_all_team_scores)
    print("Caching the private scoreboard entries...")
    cache(api.stats.get_all_team_scores_full)
    print("Caching the public scoreboard graph...")
    cache(api.stats.get_top_teams_score_progressions)
