def process(api, data):
    """
    Breakthroughs are rewarded to the first team to solve a given problem.

    Data Required: tid, pid
    """

    submissions = api.problem.get_submissions(pid=data["pid"], correctness=True)
    problem = api.problem.get_problem(pid=data["pid"])
    valid = len(submissions) == 1 and submissions[0]['tid'] == data['tid']
    return valid, {
        "name": "{} Breakthrough!".format(problem["name"]),
        "description": "Your team was the first to solve {}. Congratulations!".format(problem["name"])
    }
