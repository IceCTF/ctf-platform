"""
Problem Autogeneration Handler
"""

import api
import random
import imp
import shutil

import os
from os import path
from functools import partial
from bson import json_util
from api.common import InternalException

log = api.logger.use(__name__)

seed = ""

def is_autogen_problem(pid):
    """
    Determines whether or not a problem is autogenerated.

    Arg:
        pid: the problem id
    Returns:
        True or False whether or not the problem is autogenerated.
    """

    return api.problem.get_problem(pid=pid).get("autogen", False)

def get_metadata_path(pid, n):
    """
    Retrieve the path to the metadata file for a given problem instance.

    Args:
        pid: the problem id
        n: the instance number
    Returns:
        The metadata file path.
    """

    return path.join(get_instance_path(pid, n=n), "metadata.json")

def write_metadata(pid, n, data):
    """
    Write an autogenerated problem's instance metadata.
    This includes any fields to be overwritten from
    the original problem object.

    Args:
        pid: the problem id
        n: the instance number
        data: the metadata object
    """

    metadata_path = get_metadata_path(pid, n)
    with open(metadata_path, "w") as f:
        f.write(json_util.dumps(data))

@api.cache.fast_memoize(timeout=120)
def read_metadata(pid, n):
    """
    Reads the metadata object for a given problem instance.

    Args:
        pid: the problem id
        n: the problem instance
    Returns:
        The metadata object
    """

    metadata_path = get_metadata_path(pid, n)
    with open(metadata_path, "r") as f:
        return json_util.loads(f.read())

def build_problem_instances(pid, instances):
    """
    Build instances of an autogenerated problem.
    Required pre-competition operation for autogenerated problems
    to function correctly.

    Args:
        pid: the problem pid
        instances: the number of instances to build
    """

    problem = api.problem.get_problem(pid=pid)

    if not is_autogen_problem(pid):
        raise InternalException("{} is not flagged as an autogenerated problem.".format(problem["name"]))

    previous_state = seed_generator("INIT", pid)

    instance_path, static_instance_path = get_instance_path(pid), get_static_instance_path(pid)

    for autogen_path in [instance_path, static_instance_path]:
        log.debug("Checking for existence of '%s'...", autogen_path)
        if not path.isdir(autogen_path):
            log.debug("Created directory.")
            os.makedirs(autogen_path)

    for n in range(instances):

        log.debug("generating -> %s -> %s", problem["name"], str(n))
        build = get_generator(pid).generate(random)

        autogen_instance_path = get_instance_path(pid, n=n)

        if not path.isdir(autogen_instance_path):
            os.makedirs(autogen_instance_path)

        file_type_paths = {
            "resource_files": autogen_instance_path,
            "static_files": static_instance_path
        }

        problem_updates = build.get("problem_updates", None)

        if problem_updates is None:
            raise InternalException("Generator {} did not return a problem_update dict.".format(problem["generator"]))

        write_metadata(pid, n, problem_updates)

        for file_type, files in build.items():
            destination = file_type_paths.get(file_type, None)

            if destination is not None:

                for f, name in files:
                    if path.isfile(f):
                        shutil.copyfile(f, path.join(destination, name))

                    elif path.isdir(f):
                        shutil.copytree(f, autogen_instance_path)

        log.debug("done!")

    random.setstate(previous_state)

def get_generator_path(pid):
    """
    Gets a problem generator path.

    Args:
        pid: the problem pid
    Returns
        The path to the generator.
    """

    problem = api.problem.get_problem(pid=pid)

    if not is_autogen_problem(pid):
        raise InternalException("This problem is not autogenerated.")

    if not problem.get("generator", False):
        raise InternalException("Autogenerated problem '{}' does not have a generator.".format(problem["name"]))

    return path.join(api.problem.grader_base_path, problem["generator"])

def get_generator(pid):
    """
    Gets a handle on a problem generator module.

    Args:
        pid: the problem pid
    Returns:
        The loaded module
    """

    generator_path = get_generator_path(pid)

    if not path.isfile(generator_path):
        raise InternalException("Could not find {}.".format(generator_path))

    return imp.load_source(generator_path[:-3], generator_path)

def get_seed(pid, tid):
    """
    Get the random generator seed.

    Args:
        pid: the problem id
        tid: the team id
    Returns:
        The team's seed.
    """

    return seed + tid + pid

def seed_generator(pid, tid):
    """
    Sets python's random number generator.

    Args:
        pid: the problem id
        tid: the team id
    Returns:
        The previous state of the random generator
    """

    previous_state = random.getstate()

    random.seed(get_seed(pid, tid))

    return previous_state

@api.cache.fast_memoize(timeout=120)
def get_instance_number(pid, tid):
    """
    Maps the token to an instance number for a prolem.

    Args:
        pid: the problem id
        tid: the team id
    Returns:
        The instance number
    """

    previous_state = seed_generator(tid, pid)

    total_instances = get_number_of_instances(pid)
    if total_instances == 0:
        raise InternalException("{} has no instances.".format(pid))

    instance_number = random.randint(0, total_instances-1)
    random.setstate(previous_state)

    return instance_number

@api.cache.fast_memoize(timeout=120)
def get_number_of_instances(pid):
    """
    Gets the number of active instances of a problem.

    Args:
        pid: the problem id
    Returns:
        The number of instances.
    """

    # this is more reliable than before, but it may be a little slow
    return [dirname.isdigit() for dirname in os.listdir(get_instance_path(pid))].count(True)

def get_static_instance_path(pid):
    """
    Gets the path to the static resources of a problem.

    Args:
        pid: the problem id
    Returns:
        The path to the static resources of an autogen problem.
    """

    return path.abspath(path.join(get_instance_path(pid), "static"))

def get_instance_path(pid, n=""):
    """
    Gets the path to a particular instance of a problem.

    Args:
        n: the instance number, defaults to base of instances
        verify: Verify the path exists
    Returns:
        The path to the particular instance.
    """

    generator_path = get_generator_path(pid)
    name = api.problem.get_problem(pid)["name"]

    instance_path = path.join(path.dirname(generator_path), "instances", name, str(n))

    return path.abspath(instance_path)

@api.cache.fast_memoize(timeout=120)
def get_problem_instance(pid, tid):
    """
    Returns an instance of the autogenerated problem.

    Args:
        problem: the problem document
        tid: the tid
    Returns:
        An instance of the problem object.
    """

    problem = api.problem.get_problem(pid=pid)

    n = get_instance_number(pid, tid)

    metadata = read_metadata(pid, n)

    problem.update(metadata)

    return problem

def grade_problem_instance(pid, tid, key):
    """
    Grades an autogenerated problem. This will invoke
    the particular grader for the instance the team is mapped to.

    Args:
        pid: the problem id
        tid: the team id
        key: the team's attempted solution
    Returns:
        A dict.
        correct: boolean
        points: number of points the problem is worth
        message: a message to be returned to the user
    """

    if not is_autogen_problem(pid):
        raise InternalException("Problem is not autogenerated! {}".format(pid))

    problem = api.problem.get_problem(pid)

    n = get_instance_number(pid, tid)
    grader_problem_instance = GraderProblemInstance(pid, tid, n)

    grader = api.problem.get_grader(pid)
    correct, message = grader.grade(grader_problem_instance, key)

    return {
        "correct": correct,
        "points": problem["score"],
        "message": message
    }

class GraderProblemInstance(object):
    """
    Represents the instances of an autogenerated problem.
    """

    def __init__(self, pid, tid, n):

        self.instance = n

        self.get_instance_path = partial(get_instance_path, pid, n=n)
        self.seed_generator = partial(seed_generator, pid, tid)

        self.write_metadata = partial(write_metadata, pid, n)
        self.read_metadata = partial(read_metadata, pid)
