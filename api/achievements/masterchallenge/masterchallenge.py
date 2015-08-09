def process(api, data):
    pid = data["pid"]
    master_challenges = {
        "sausages": "bf9cee6ef204cf043be970dcd4837fa4",
        "giga": "5262457500d337190c0f3484701a4ca6",
        "mondrian": "db7ef43550856247226e9b1423671b77",
        "wiki2": "ccb44839ee47cdf92c3f55c3e596801c",
        "alternate_rsa": "4f902c78957792f1fa6552719ff40997",
        "supernote": "13ce1fe752f4ad502bab81c312bf806b"
    }
    return pid in master_challenges.values()