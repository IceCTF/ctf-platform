#!/usr/bin/python3
"""
Problem management script.
"""

import argparse
import sys
import json

import api
from api.common import APIException

from os.path import isfile
from bson import json_util

api.common.mongo_addr = "127.0.0.1"
api.common.mongo_port = 27017
api.common.mongo_db_name = "pico"

def insert_problems(files):
    for contents in files.values():
        for line in contents:
            try:
                api.problem.insert_problem_from_json(line.strip())
            except APIException as error:
                raise
                exit(1)
    errors = api.problem.analyze_problems()
    for error in errors:
        print(error)

def migrate_problems(files, output_file, debug):

    migration_key = {
        "displayname": "name",
        "basescore": "score",
        "desc": "description",
        "relatedproblems": "related_problems"
    }

    migration_overwrites = {
        "grader": "test.py"
    }

    deletion_key = ["_id", "pid", "generator", "submissiontype", "devnotes"]

    problems = []
    output = ""
    for contents in files.values():
        for line in contents:
            problem = json_util.loads(line.strip())
            problems.append(problem)

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
    parser = argparse.ArgumentParser(description='picoCTF problem manager')

    #TODO: Implement these?
    #parser.add_argument("-l", action="store_true", dest="show_list", help="View problem list")
    #parser.add_argument("-f", action="append", default=[], dest="filters", help="Key:value pairs that are used to search the database for problems. Used in conjuction with -l.")

    parser.add_argument("-m", action="store_true", dest="migrate", help="Migrate old 2013 problems to new format.", default=False)
    parser.add_argument("-d", action="store_true", dest="debug", help="Debug mode", default=False)
    parser.add_argument("-o", action="store", dest="output_file", help="Output file.", default=sys.stdout)
    parser.add_argument("--no-confirm", action="store_true", dest="no_confirm", help="Remove confirmation and assume default action.")
    parser.add_argument("--drop-problems", action="store_true", help="Remove all problems in the database.")

    parser.add_argument("files", nargs="*", help="Files containing problems to insert.")

    args = parser.parse_args()

    files = {}

    #Check that all listed files exist.
    for file_path in args.files:
        if not isfile(file_path):
            print("{}: File does not exist!".format(file_path))
            exit(1)
        with open(file_path, "r") as f:
            files[file_path] = f.readlines()

    output_file = get_output_file(args.output_file)

    if args.drop_problems:
        if not args.no_confirm:
            #TODO: make me pretty
            answer = input("Are you sure you want to drop the problem's collection? [y/n]")
            if answer.lower() != "y":
                exit(1)

        db = api.common.get_conn()
        db.problems.remove()
        print("Removed all of the problems.")

    if args.migrate:
        migrate_problems(files, output_file, args.debug)
    else:
        insert_problems(files)
main()
