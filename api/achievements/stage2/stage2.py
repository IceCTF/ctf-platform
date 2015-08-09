def process(api, data):
    pid = data["pid"]
    stage = {
        "Open Sesame": "026cd71be5149e4c645a45b4915d9917",
        "Overflow 1": "0b944e114502bd1af14469dbb51b9572",
        "Overflow 2": "ee876f0736c4fe1b5607b68098f4cc1c",
        "Simple": "1fbb1e3943c2c6c560247ac8f9289780",
        "Diary": "edcf7eb3a7d5eab2be6688cb3e59fcee",
        "Farm Animals": "956441e1e973c3bd0a34d6991b5ac28b",
        "Numb3rs": "e30ecef3cbbab794c809f219eddadba8",
        "Document Troubles": "dded365363e42ab2aa379d7675dfc849",
        "Scan Me": "d36a6d075a8bc5b5d63423d6fd40099e",
        "SHARKNADO!": "a656827139fffc0d9c8f26a353d64cbd",
        "Statistics": "c33e404a441c6ba9648f88af3c68a1ca",
        "Bomb!": "763420a82e74a0e0f7af734c6334ef2c",
        "Giffy": "dfc4e89f4369ac8d6a92e8893b54fa51",
        "Injection": "548bb431406ebb2d5ba9dd380ede692a",
        "SQL Injection 1": "8dfc2dd7c2bdb05ac64e15a23339f113"
    }
    pids = api.problem.get_solved_pids(tid=data['tid'])
    earned = True
    for pid in stage.values():
        if pid not in pids:
            earned = False
    return earned, {}