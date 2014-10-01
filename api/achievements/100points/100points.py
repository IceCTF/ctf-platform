def process(api, data):
    return api.stats.get_score(tid=data["tid"]) > 100, {}
