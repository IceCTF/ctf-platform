def process(api, tid, uid):
    return api.stats.get_score(tid=tid) > 100
