"""
Problem Testing Module
"""

import pytest
import re

import api

from api.common import APIException
from common import clear_collections, ensure_empty_collections, clear_cache
from conftest import setup_db, teardown_db

class TestProblems(object):
    """
    API Tests for problem.py
    """

    test_user = {
        "username": "valid",
        "password": "valid",
        "email": "test@hs.edu",
        "create-new-team": "true",

        "team-name-new": "test",
        "team-adv-name-new": "test",
        "team-adv-email-new": "hacks@hs.edu",
        "team-school-new": "Hacks HS",
        "team-password-new": "leet_hax"
    }

    # create 5 base problems
    base_problems = [
        {
            "name" : "base-" + str(i),
            "score" : 10,
            "category": "",
            "grader" : "test.py",
            "description" : "",
            "autogen": False,
            "threshold" : 0
        }
        for i in range(5)
    ]

    # create 5 disabled problems
    disabled_problems = [
        {
            "name" : "locked-" + str(i),
            "score" : 10,
            "category": "",
            "grader" : "test.py",
            "autogen": False,
            "description" : "",
            "threshold" : 0,
            "disabled": True
        }
        for i in range(5)
    ]

    def generate_problems(base_problems):
        """A workaround for python3's list comprehension scoping"""

        # create 5 level1 problems
        level1_problems = [
            {
                "name" : "level1-" + str(i),
                "score" : 60,
                "category": "",
                "grader" : "test.py",
                "description" : "",
                "autogen": False,
                "threshold" : 3,
                "weightmap" : {p['name']: 1 for p in base_problems}
            }
            for i in range(5)
        ]

        return level1_problems

    level1_problems = generate_problems(base_problems)

    enabled_problems = base_problems + level1_problems
    all_problems = enabled_problems + disabled_problems


    autogen_problems = [
        {
                "name" : "autogen-" + str(i),
                "score" : 2**i,
                "category": "autogen",
                "grader" : "autogentest/grader.py",
                "generator" : "autogentest/generator.py",
                "description" : "",
                "threshold": 0,
                "autogen": True,
        }
        for i in range(10)
    ]

    # test keys
    correct = "test"
    wrong = "wrong"

    def setup_class(self):
        """
        Class setup code
        """

        setup_db()

        # initialization code
        self.uid = api.user.create_user_request(self.test_user)
        self.tid = api.user.get_team(uid=self.uid)['tid']

        # insert all problems
        self.pids = []
        for problem in self.all_problems:
            pid = api.problem.insert_problem(problem)
            self.pids.append(pid)


        self.base_pids =  [p['pid'] for p in self.base_problems]
        self.enabled_pids = [p['pid'] for p in self.enabled_problems]
        self.disabled_pids = [p['pid'] for p in self.disabled_problems]
        self.all_pids = self.enabled_pids + self.disabled_pids

    def teardown_class(self):
        teardown_db()

    def test_insert_problems(self):
        """
        Tests problem insertion.

        Covers:
            problem.insert_problem
            problem.get_problem
            problem.get_all_problems
        """

        # problems were inserted in initialization - try to insert the problems again
        for problem in self.all_problems:
            with pytest.raises(APIException):
                api.problem.insert_problem(problem)
                assert False, "Was able to insert a problem twice."

        # verify that the enabled problems match
        db_problems = api.problem.get_all_problems()
        for problem in db_problems:
            assert problem['pid'] in self.enabled_pids, "Problems do not match"
            assert problem['pid'] not in self.disabled_pids, "Problem should not be enabled"

        # verify that the disabled problems match
        db_all_problems = api.problem.get_all_problems(show_disabled=True)
        for problem in db_problems:
            assert problem['pid'] in self.all_pids

    @ensure_empty_collections("submissions")
    @clear_collections("submissions")
    @clear_cache()
    def test_submissions(self):
        """
        Tests key submissions.

        Covers:
            problem.submit_key
            problem.get_submissions
            problem.get_team_submissions
        """

        # test correct submissions
        for problem in self.base_problems[:2]:
            result = api.problem.submit_key(self.tid, problem['pid'], self.correct, uid=self.uid)
            assert result['correct'], "Correct key was not accepted"
            assert result['points'] == problem['score'], "Did not return correct score"

            solved = api.problem.get_solved_problems(self.tid)
            assert api.problem.get_problem(pid=problem['pid']) in solved

        # test incorrect submissions
        for problem in self.base_problems[2:]:
            result = api.problem.submit_key(self.tid, problem['pid'], self.wrong, uid=self.uid)
            assert not result['correct'], "Incorrect key was accepted"
            assert result['points'] == problem['score'], "Did not return correct score"

            solved = api.problem.get_solved_problems(self.tid)
            assert api.problem.get_problem(pid=problem['pid']) not in solved

        # test submitting correct twice
        with pytest.raises(APIException):
            api.problem.submit_key(self.tid, self.base_problems[0]['pid'], self.correct, uid=self.uid)
            assert False, "Submitted key to problem that was already solved"

        # test submitting to disabled problem
        with pytest.raises(APIException):
            api.problem.submit_key(self.tid, self.disabled_problems[0]['pid'], self.correct, uid=self.uid)
            assert False, "Submitted key to disabled problem"

        # test getting submissions two ways
        assert len(api.problem.get_submissions(uid=self.uid)) == len(self.base_problems)
        assert len(api.problem.get_submissions(tid=self.tid)) == len(self.base_problems)

    @ensure_empty_collections("submissions")
    @clear_collections("submissions")
    @clear_cache()
    def test_get_unlocked_problems(self):
        """
        Tests getting the unlocked problems

        Covers:
            problem.get_unlocked_problems
            problem.submit_key
        """

        # check that base problems are unlocked
        unlocked = api.problem.get_unlocked_problems(self.tid)
        unlocked_pids = [p['pid'] for p in unlocked]
        for pid in self.base_pids:
            assert pid in unlocked_pids, "Base problem didn't unlock"

        # unlock more problems
        for problem in self.base_problems[:3]:
            api.problem.submit_key(self.tid, problem['pid'], self.correct, uid=self.uid)

        unlocked = api.problem.get_unlocked_problems(self.tid)
        unlocked_pids = [p['pid'] for p in unlocked]

        for problem in unlocked:
            assert problem['pid'] not in self.disabled_pids, "Disabled problem is unlocked"

        for pid in self.enabled_pids:
            assert pid in unlocked_pids, "Level1 problem didn't unlock"

    @ensure_empty_collections("submissions")
    @clear_collections("submissions", "problems") #clear problems for test_autogen
    @clear_cache()
    def test_scoring(self):
        correct_total = 0
        for problem in self.base_problems + self.level1_problems:
            score = api.problem.submit_key(self.tid, problem['pid'], self.correct, uid=self.uid)['points']
            correct_total += problem['score']
            assert score == problem['score'], "submit_key return wrong score"
            s = api.stats.get_score(tid=self.tid)
            assert api.stats.get_score(tid=self.tid) == correct_total, "Team score is calculating incorrectly!"
            assert api.stats.get_score(uid=self.uid) == correct_total, "User score is calculating incorrectly!"


    @ensure_empty_collections("submissions", "problems")
    @clear_cache()
    def test_autogen(self):
        """
        Tests the insertion, generation, and grading of autogenerated problems.

        Covers:
            problem.insert_problem
            autogen.build_problem_instances
            problem.grade_problem
            autogen.grade_problem_instance

            autogen.*
        """

        autogen_pids = [api.problem.insert_problem(p) for p in self.autogen_problems]

        score = 0
        for pid in autogen_pids:
            api.autogen.build_problem_instances(pid, 10)

            instance = api.autogen.get_problem_instance(pid, self.tid)
            key = re.search(r'\d+', instance["description"]).group()

            assert api.problem.submit_key(self.tid, pid, key, uid=self.uid)["correct"], "Autogen flag not accepted!"
            score += instance["score"]
            assert api.stats.get_score(tid=self.tid) == score
