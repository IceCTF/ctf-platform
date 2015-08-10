def process(api, data):
    pid = data["pid"]
    master_challenges = {
        "SuperNote": "13ce1fe752f4ad502bab81c312bf806b",
        "Alternate RSA": "4f902c78957792f1fa6552719ff40997",
        "Sausages": "bf9cee6ef204cf043be970dcd4837fa4",
        "Mondrian": "db7ef43550856247226e9b1423671b77",
        "Giga": "5262457500d337190c0f3484701a4ca6",
        "Wiki & The Furious": "ccb44839ee47cdf92c3f55c3e596801c"
    }
    return pid in master_challenges.values(), {}