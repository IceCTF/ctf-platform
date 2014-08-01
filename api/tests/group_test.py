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
from conftest import setup_db, teardown_db

class TestGroups(object):
    """
    API Tests for group.py
    """

    teacher_user = {
        "username": "valid",
        "password": "valid",
        "email": "valid@hs.edu",
        "create-new-teacher": True,
        "teacher-school": "Hacks HS"
    }

    base_teams = [
        {
            "team_name": "team" + str(i),
            "adviser_name": "Dr. Test",
            "adviser_email": "test@hs.edu",
            "school": "Test HS",
            "password": "much_protected"
        }
        for i in range(5)
    ]

    base_group = {
        "group-name": "group",
    }

    def setup_class(self):
        setup_db()

        # create teams
        self.tids = []
        for team in self.base_teams:
            self.tids.append(api.team.create_team(team))

        self.owner_uid = api.user.create_user_request(self.teacher_user)
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
            gids.append(api.group.create_group_request(group, tid=self.owner_tid))

        assert len(set(gids)) == len(gids), "gids are not unique."

        assert len(api.team.get_groups(tid=self.owner_tid)) == len(gids), "Not all groups were created."

        for i, gid in enumerate(gids):
            name = self.base_group['group-name'] + str(i)

            group_from_gid = api.group.get_group(gid=gid)
            group_from_name = api.group.get_group(name=name)

            assert group_from_gid == group_from_name, "Group lookup from gid and name are not the same."

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

        gid = api.group.create_group_request(self.base_group, self.owner_tid)
        name = api.group.get_group(gid=gid)["name"]

        params = {"group-name": name}

        for tid in self.tids:
            if tid is not self.owner_tid:
                api.group.join_group_request(params, tid)
                assert tid in api.group.get_group(gid=gid)['members']

        for tid in self.tids:
            api.group.leave_group_request(params, tid)
            assert tid not in api.group.get_group(gid=gid)['members']

        with pytest.raises(WebException):
            api.group.leave_group_request(params, self.owner_tid)
            assert False, "Was able to leve group twice!"
