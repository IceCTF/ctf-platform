#!/usr/bin/python3
"""
Problem management script.
"""

import argparse
import sys
import logging
import api
from api.common import APIException, InternalException

from os import path
from bson import json_util


def check_files_exist(files):
    for f in files:
        if not path.isfile(f):
            logging.critical("No such file {}".format(f))
            return False
    return True


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
    for f in files:
        contents = open(f, "r").read()
        data = json_util.loads(contents)
        if isinstance(data, list):
            objects += data
        elif isinstance(data, dict):
            objects.append(data)
        else:
            logging.warning("JSON file {} did not contain an object or list of objects".format(f))
    return objects


def migrate_problems(args):
    files = args.files
    output_file = args.output

    if not check_files_exist(files):
        return

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


def build_autogen(args):
    instances = args.instance_count
    problems = api.problem.get_all_problems(show_disabled=True)
    for problem in problems:
        if problem.get("autogen", False):
            api.autogen.build_problem_instances(problem["pid"], instances)


def list_problems(args):
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
            logging.warning(error)
            exit(1)


def add_new_problems(args):
    if check_files_exist(args.files):
        insert_objects(api.problem.insert_problem, args.files)
        errors = api.problem.analyze_problems()
        for error in errors:
            logging.warning(error)


def add_new_achievements(args):
    if check_files_exist(args.files):
        insert_objects(api.achievement.insert_achievement, args.files)


def main():
    parser = argparse.ArgumentParser(description="{} problem manager".format(api.config.competition_name))
    debug_level = parser.add_mutually_exclusive_group()
    debug_level.add_argument('-v', '--verbose', help="Print intermediate results", action="store_true")
    debug_level.add_argument('-s', '--silent', help="Print out very little", action="store_true")
    subparser = parser.add_subparsers(help='Select one of the following actions')

    # Autogen
    parser_autogen = subparser.add_parser('autogen', help='Deal with Problem Autogeneration')
    subparser_autogen = parser_autogen.add_subparsers(help='Select one of the following actions')

    parser_autogen_build = subparser_autogen.add_parser('build', help='Build new autogen instances')
    parser_autogen_build.add_argument("instance_count", nargs=1, help="How many instances of each problem to build")
    parser_autogen_build.set_defaults(func=build_autogen)

    # Problems
    parser_problems = subparser.add_parser('problems', help='Deal with Problems')
    subparser_problems = parser_problems.add_subparsers(help='Select one of the following actions')

    parser_problems_load = subparser_problems.add_parser('load', help='Load problems into the database')
    parser_problems_load.add_argument("files", nargs="+", help="Files containing problems to insert.")
    parser_problems_load.set_defaults(func=add_new_problems)

    parser_problems_list = subparser_problems.add_parser('list', help='List problems in the database')
    parser_problems_list.set_defaults(func=list_problems)

    parser_problems_migrate = subparser_problems.add_parser('migrate', help='Migrate 2013 problems to the new format')
    parser_problems_migrate.add_argument('-o', '--output', action="store", help="Output file.", default=sys.stdout)
    parser_problems_migrate.set_defaults(func=migrate_problems)

    # Achievements
    parser_achievements = subparser.add_parser('achievements', help='Deal with Achievements')
    subparser_achievements = parser_achievements.add_subparsers(help='Select one of the following actions')

    parser_achievements_load = subparser_achievements.add_parser('load', help='Load new achievements into the database')
    parser_achievements_load.add_argument("files", nargs="+", help="Files containing achievements to insert.")
    parser_achievements_load.set_defaults(func=add_new_achievements)

    args = parser.parse_args()
    if args.silent:
        logging.basicConfig(level=logging.CRITICAL, stream=sys.stdout)
    elif args.verbose:
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    else:
        logging.basicConfig(level=logging.WARNING, stream=sys.stdout)

    if 'func' in args:
        args.func(args)
    else:
        parser.print_help()

main()
