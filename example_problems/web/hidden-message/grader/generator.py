from os import path
from hashlib import sha1

def generate(random, pid, autogen_tools, n):
    """
    Generate an instance of the problem
    Needs to return a list of files to copy to particular instance.
    """

    #Get a random build path
    generator_path = autogen_tools.get_directory(__file__)

    template_path = path.join(generator_path, "website.html.template")
    rendered_template_path = path.join(generator_path, "website.html")

    key = "my_key_here"
    flag = "flag_" + sha1((str(n) + key).encode('utf-8')).hexdigest()

    autogen_tools.replace_source_tokens(
        template_path,
        {"flag": flag},
        rendered_template_path
    )

    homepage_link = autogen_tools.generate_resource_link(pid, "website.html", title="odd website")

    return {
        "resource_files": {
            "public": [
                (rendered_template_path, "website.html"),
            ],
        },
        "static_files": {
        },
        "problem_updates": {
            "description": "Have you seen this %s? Maybe something is hidden there..." % homepage_link
        }
    }
