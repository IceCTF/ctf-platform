"""
Autogen example.
"""

from os import path

def grade(autogen, key):

    key_path = path.join(autogen.get_instance_path(), "key")

    f = open(key_path)
    flag = f.read().strip()
    f.close()

    if flag == key:
        return (True, "Autogen!")
    else:
        return (False, ":<")

