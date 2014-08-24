#!/usr/bin/python3
"""
Problem management script.
"""

import argparse
import sys
import imp
import random
import shutil
import os

import api
from api.common import APIException, InternalException

from os import path
from bson import json_util

def insert_objects(f, files):
    objects = get_json_objects(files)
    for obj in objects:
        try:
            f(obj)
        except APIException as error:
            raise
            exit(1)

def get_json_objects(files):
    objects = []
    for contents in files.values():
        for line in contents:
            obj = json_util.loads(line.strip())
            objects.append(obj)
    return objects

def migrate_problems(files, output_file, debug):

    migration_key = {
        "displayname": "name",
        "basescore": "score",
        "desc": "description",
        "relatedproblems": "related_problems"
    }

    migration_overwrites = {
        "grader": "test.py",
        "autogen": False
    }

    deletion_key = ["_id", "pid", "generator", "submissiontype", "devnotes"]

    problems = get_json_objects(files)
    output = ""

    def get_display_name_from_pid(problems, pid):
        for problem in problems:
            if problem.get("pid") == pid:
                return problem.get("displayname")

    for problem in problems:
        if problem.get("weightmap"):
            new_map = {}
            for pid, num in problem["weightmap"].items():
                name = get_display_name_from_pid(problems, pid)
                new_map[name] = num
            problem["weightmap"] = new_map

    for problem in problems:
        if "desc" not in problem:
            problem["desc"] = "I'm bad."

        for key in list(problem.keys()):

            if key in migration_key:
                problem[migration_key[key]] = problem[key]

            if key in migration_overwrites:
                problem[key] = migration_overwrites[key]

            if key in migration_key or key in deletion_key:
                problem.pop(key, None)
        output += json_util.dumps(problem) + "\n"
    output_file.write(output)

def build_autogen(instances):
    problems = api.problem.get_all_problems(show_disabled=True)
    for problem in problems:
        if problem.get("autogen", False):
            api.autogen.build_problem_instances(problem["pid"], instances)

def list_problems():
    #TODO: This could be improved
    problems = api.problem.get_all_problems(show_disabled=True)
    for problem in problems:
        print("{} ({}) - {} points".format(problem["name"], "disabled" if problem["disabled"] else "enabled", problem["score"]))

def drop_collections(collections):
    db = api.common.get_conn()
    for collection in collections:
        db[collection].remove()

def get_output_file(output):
    if output == sys.stdout:
        return output
    else:
        try:
            return open(output, "w")
        except IOError as error:
            print(error)
            exit(1)

def main():
    parser = argparse.ArgumentParser(description="{} problem manager".format(api.config.competition_name))


    parser.add_argument("-l", action="store_true", dest="show_list", help="View problem list")
    #TODO: Implement this?
    #parser.add_argument("-f", action="append", default=[], dest="filters", help="Key:value pairs that are used to search the database for problems. Used in conjuction with -l.")
    parser.add_argument("-m", action="store_true", dest="migrate", help="Migrate old 2013 problems to new format.", default=False)
    parser.add_argument("-b", "--build-autogen", action="store", type=int, help="Generate a specified amount of instances for a given list of problems.", default=0)
    parser.add_argument("-d", action="store_true", dest="debug", help="Debug mode", default=False)
    parser.add_argument("-o", action="store", dest="output_file", help="Output file.", default=sys.stdout)
    parser.add_argument("--no-confirm", action="store_true", dest="no_confirm", help="Remove confirmation and assume default action.")
    parser.add_argument("-a", action="store_true", dest="achievements", help="Assume files contain achievements.")
    parser.add_argument("-c", "--drop-collections", dest="collections_string", action="store", help="Remove all entries from the listed collections in the database.")

    parser.add_argument("files", nargs="*", help="Files containing problems to insert.")

    args = parser.parse_args()

    files = {}

    if args.collections_string:
        collections = map(lambda s: s.strip(), args.collections_string.split(","))
        drop_collections(collections)
        exit(0)
    if args.build_autogen > 0:
        build_autogen(args.build_autogen)
        exit(0)
    if args.show_list:
        list_problems()
        exit(0)

    #Check that all listed files exist.
    if len(args.files) == 0:
        parser.print_help()
        exit(1)

    for file_path in args.files:
        if not path.isfile(file_path):
            print("{}: File does not exist!".format(file_path))
            exit(1)
        with open(file_path, "r") as f:
            files[file_path] = f.readlines()

    if args.migrate:
        output_file = get_output_file(args.output_file)
        migrate_problems(files, output_file, args.debug)
    else:
        if args.achievements:
            insert_objects(api.achievement.insert_achievement, files)
        else:
            insert_objects(api.problem.insert_problem, files)
            errors = api.problem.analyze_problems()
            for error in errors:
                print(error)
main()
