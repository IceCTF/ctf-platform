"""
Group Testing Module
"""

import pytest
import api.user
import api.team
import api.common
import bcrypt

from api.common import WebException, InternalException
from common import clear_collections, ensure_empty_collections
from common import teacher_user
from conftest import setup_db, teardown_db

class TestGroups(object):
    """
    API Tests for group.py
    """

    base_teams = [
        {
            "team_name": "team" + str(i),
            "school": "Test HS",
            "password": "much_protected"
        }
        for i in range(5)
    ]

    base_group = {
        "group-owner": teacher_user["username"],
        "group-name": "group_yo"
    }

    def setup_class(self):
        setup_db()

        # create teams
        self.tids = []
        for team in self.base_teams:
            self.tids.append(api.team.create_team(team))

        self.owner_uid = api.user.create_user_request(teacher_user)
        self.owner_tid = api.user.get_team(uid=self.owner_uid)['tid']

    def teardown_class(self):
        teardown_db()

    @ensure_empty_collections("groups")
    @clear_collections("groups")
    def test_create_batch_groups(self, groups=10):
        """
        Tests group creation and lookups

        Covers:
            group.create_group_request
            group.get_group

        """

        gids = []
        for i in range(groups):
            group = self.base_group.copy()
            group["group-name"] += str(i)
            gids.append(api.group.create_group_request(group, uid=self.owner_uid))

        assert len(api.team.get_groups(uid=self.owner_uid, tid=self.owner_tid)) \
            == len(gids), "Not all groups were created."

        with pytest.raises(InternalException):
            api.group.get_group(gid="Not a real gid")
            assert False, "Looked up group with invalid gid!"

        with pytest.raises(InternalException):
            api.group.get_group(name="Not a real name")
            assert False, "Looked up group with invalid name!"

    @ensure_empty_collections("groups")
    @clear_collections("groups")
    def test_join_and_leave_group(self):
        """
        Tests leaving and joining groups

        Covers:
            group.create_group_request
            group.get_group
            group.join_group
            group.leave_group
        """

        gid = api.group.create_group_request(self.base_group, self.owner_uid)
        name = api.group.get_group(gid=gid)["name"]

        params = {"group-name": name, "group-owner": teacher_user["username"]}

        for tid in self.tids:
            if tid is not self.owner_tid:
                api.group.join_group_request(params, tid)
                assert tid in api.group.get_group(gid=gid)['members']

        for tid in self.tids:
            api.group.leave_group_request(params, tid)
            assert tid not in api.group.get_group(gid=gid)['members']

        with pytest.raises(WebException):
            api.group.leave_group_request(params, self.owner_tid)
            assert False, "Was able to leave group twice!"
