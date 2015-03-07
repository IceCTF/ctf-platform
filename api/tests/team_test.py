"""
Team Testing Module
"""

import pytest
import api.user
import api.team
import api.common
import bcrypt

from api.common import WebException, InternalException
from common import clear_collections, ensure_empty_collections
from common import base_team, base_user
from conftest import setup_db, teardown_db

class TestTeams(object):
    """
    API Tests for team.py
    """

    def setup_class(self):
        setup_db()

    def teardown_class(self):
        teardown_db()

    @ensure_empty_collections("teams")
    @clear_collections("teams")
    def test_create_batch_teams(self, teams=10):
        """
        Tests team creation.

        Covers:
            team.create_team
            team.get_team
            team.get_all_teams
        """
        tids = []
        for i in range(teams):
            team = base_team.copy()
            team["team_name"] += str(i)
            tids.append(api.team.create_team(team))

        assert len(set(tids)) == len(tids), "tids are not unique."

        assert len(api.team.get_all_teams()) == len(tids), "Not all teams were created."

        for i, tid in enumerate(tids):
            name = base_team['team_name'] + str(i)

            team_from_tid = api.team.get_team(tid=tid)
            team_from_name = api.team.get_team(name=name)

            assert team_from_tid == team_from_name, "Team lookup from tid and name are not the same."

    @ensure_empty_collections("teams", "users")
    @clear_collections("teams", "users")
    def test_get_team_uids(self):
        """
        Tests the code that retrieves the list of uids on a team

        Covers:
            team.create_team
            user.create_user_request
            team.get_team_uids
        """

        tid = api.team.create_team(base_team.copy())

        uids = []
        for i in range(api.team.max_team_users):
            test_user = base_user.copy()
            test_user['username'] += str(i)
            uids.append(api.user.create_user_request(test_user))

        team_uids = api.team.get_team_uids(tid)
        assert len(team_uids) == api.team.max_team_users, "Team does not have correct number of members"
        assert sorted(uids) == sorted(team_uids), "Team does not have the correct members"

    @ensure_empty_collections("teams", "users")
    @clear_collections("teams", "users")
    def test_create_user_request_team_size_validation(self):
        """
        Tests the team size restriction

        Covers:
            team.create_team
            user.create_user_request
        """

        api.team.create_team(base_team.copy())

        uid = None
        for i in range(api.team.max_team_users):
            test_user = base_user.copy()
            test_user['username'] += str(i)
            uid = api.user.create_user_request(test_user)

        with pytest.raises(WebException):
            api.user.create_user_request(base_user.copy())
            assert False, "Team has too many users"

        api.user.disable_account(uid)

        #Should be able to add another user after disabling one.
        test_user = base_user.copy()
        test_user['username'] += "addition"
        api.user.create_user_request(test_user)
