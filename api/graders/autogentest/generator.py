"""
Generator example.
"""

def generate(random):
    """
    Generate an instance of the problem

    Needs to return a list of files to copy to particular instance.
    """

    f = open("/tmp/key", "w")

    f.write(random.randint(0, 1000))

    f.close()

    return ["/tmp/key"]


