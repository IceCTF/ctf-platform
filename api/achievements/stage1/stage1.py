def process(api, data):
    pid = data["pid"]
    stage = {
        "Cryptic Crypto": "04d12237b73ad8d67a2182028ebb88fd",
        "Numeric": "87322391cc6e8948ce9fd5d6cb84fced",
        "ROT13": "94ab9cf0961517dd4a0b796054493038",
        "Logoventures": "4bbd2bfca791fa2264250edff79e45d4",
        "Logoventures 2: Reloaded": "f7cdd390a0e8d3f5533503202f42b5ac",
        "Warm Up": "c43b8936d87c59ac728112888946129c",
        "Facebook": "d85544fce402c7a2a96a48078edaf203",
        "Not Found": "9d1ead73e678fa2f51a70a933b0bf017",
        "Liar": "1cbd3b9800b88f9cb98755e40a15c813",
        "Oh No!": "6f256632fcf2f334335d0391eb53ad91"
    }
    pids = api.problem.get_solved_pids(tid=data['tid'])
    earned = True
    for pid in stage.values():
        if pid not in pids:
            earned = False
    return earned, {}