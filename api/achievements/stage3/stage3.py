def process(api, data):
    pid = data["pid"]
    stage = {
        "Yee-Haw Cowboy!": "b3fb0e84348c3381c64a2a1eaa9614a4",
        "Fermat": "8602d8eeb9527dbdbd36743672a730a2",
        "fsociety": "926782667597d71479677e8aab0ad4dc",
        "Onions have layers": "76a0ebbf477c02216eafc0d57fe23e5d",
        "PyShell": "7a42b5baaaafde3a5487722f1fb8913e",
        "Shocked!": "16ddd9a3a3705ca035acf74ea5db352d",
        "2x0r": "9c61fd4f2ab4623498fe0f3d3c0cc9c8",
        "Entropy": "15fc3950b7c08c0b533f05a119795393",
        "RSA": "445d0434ad7b42aff5bab616ebb41970",
        "RSA3": "df94084b1a1e231de2cab3ded0b52a9f",
        "Epilepsy Warning": "10625dcaa666928f88789b6e94b393c9",
        "Husavik": "bdf0c11a04ca505f33a8b510af0830a1",
        "Ryan Gooseling": "fbfc4903d6b09c433afbedb75df97940",
        "NULL": "6c3e226b4d4795d518ab341b0824ec29",
        "Barista": "927cfca0fee90d0f559853f489a98d29",
        "Hackers in disguise": "33601880756b3d37e0e26aeb6e773604",
        "Wiki": "bf111e3622a72a3b5dc784b5903983ca"
    }
    pids = api.problem.get_solved_pids(tid=data['tid'])
    earned = True
    for pid in stage.values():
        if pid not in pids:
            earned = False
    return earned, {}