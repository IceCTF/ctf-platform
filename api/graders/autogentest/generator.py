"""
Generator example.
"""

def generate(random):
    """
    Generate an instance of the problem

    Needs to return a list of files to copy to particular instance.
    """

    f = open("/tmp/key", "w")

    k = str(random.randint(0, 1000))
    f.write(k)
    f.close()

    return {
        "resource_files": [("/tmp/key", "key")],
        "static_files": [("/tmp/key", "backdoor")],
        "problem_updates": {
            "description": "The answer is not "+k+". ;)"
        }
    }


