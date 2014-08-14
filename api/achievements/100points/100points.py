def process(api, tid, uid, pid):
    return api.stats.get_score(tid=tid) > 100
