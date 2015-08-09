def process(api, data):
    pid = data["pid"]
    stage = {
        "Elevate": "776230964121ff9df74a3a4ef6bd40d6",
        "SuperNote": "13ce1fe752f4ad502bab81c312bf806b",
        "Agents": "375099f0c804e924c1dc275370710d92",
        "Alternate RSA": "4f902c78957792f1fa6552719ff40997",
        "Sausages": "bf9cee6ef204cf043be970dcd4837fa4",
        "Mondrian": "db7ef43550856247226e9b1423671b77",
        "Authorize": "7f83df9cd29577d544efd9ff66d7118a",
        "Giga": "5262457500d337190c0f3484701a4ca6",
        "Wiki & The Furious": "ccb44839ee47cdf92c3f55c3e596801c",
    }
    pids = api.problem.get_solved_pids(tid=data['tid'])
    for pid in stage.values():
        if pid not in pids:
            return False, {}
    return True, {}