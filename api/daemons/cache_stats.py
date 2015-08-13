#!/usr/bin/python3

import api
import time, sys

def cache(f, *args, **kwargs):
    result = f(cache=False, *args, **kwargs)
    key = api.cache.get_mongo_key(f, *args, **kwargs)
    api.cache.set(key, result)

def run():
    print("Caching the contestant scoreboard entries...")
    cache(api.stats.get_all_team_scores)
    print("Caching the total scoreboard entries...")
    cache(api.stats.get_all_team_scores, show_ineligible=True)
    print("Caching the contestant scoreboard graph...")
    cache(api.stats.get_top_teams_score_progressions)
    print("Caching the total scoreboard graph...")
