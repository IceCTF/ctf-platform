def process(api, data):
    """
    Breakthroughs are rewarded to the first team to solve a given problem.

    Data Required: tid, pid
    """

    submissions = api.problems.get_problem_submissions(data["pid"], True)
    problem = api.problem.get_problem(pid=data["pid"])
    return len(submissions) == 0, {
        "name": "{} Breakthrough!".format(problem["name"]),
        "description": "Your team was the first to solve {}. Congratulations!".format(problem["name"])
    }
