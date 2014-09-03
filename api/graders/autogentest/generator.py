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
        "resource_files": {
            "public": [("/tmp/key", "key")],
            "private": [("/tmp/key", "private_key")]
        },
        "static_files": {
            "public": [("/tmp/key", "public_static")],
            "private": [("/tmp/key", "private_static")]
        },
        "problem_updates": {
            "description": "The answer is not "+k+". ;)"
        }
    }
