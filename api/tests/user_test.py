"""
User Testing Module
"""

import pytest
import bcrypt

import api.user
import api.common
import api.team

from api.common import safe_fail, WebException
from common import clear_collections, ensure_empty_collections
from conftest import setup_db, teardown_db

class TestUsers(object):
    """
    API Tests for user.py
    """

    teacher_user = {
        "username": "valid",
        "password": "valid",
        "email": "valid@hs.edu",
        "create-new-teacher": "true",
        "teacher-school": "Hacks HS"
    }

    new_team_user = {
        "username": "valid",
        "password": "valid",
        "email": "valid@hs.edu",
        "create-new-team": "true",

        "team-name-new": "Valid Hacks",
        "team-adv-name-new": "Dr. Hacks",
        "team-adv-email-new": "hacks@hs.edu",
        "team-school-new": "Hacks HS",
        "team-password-new": "leet_hax"
    }

    existing_team_user = {
        "username": "valid",
        "password": "valid",
        "email": "valid@hs.edu",
        "create-new-team": "false",

        "team-password-existing": "leet_hax",
        "team-name-existing": "massive_hacks"
    }

    #TB: This is sort of also testing team.py. Is there a better way to seperate these?
    base_team = {
        "team_name" : "massive_hacks",
        "adviser_name": "Dr. Hacks",
        "adviser_email": "hacks@hs.edu",
        "school": "Hacks HS",
        "password": "leet_hax"
    }

    def setup_class(self):
        setup_db()

    def teardown_class(self):
        teardown_db()

    @ensure_empty_collections("users", "teams")
    @clear_collections("users", "teams")
    def test_create_batch_users(self, users=10):
        """
        Tests user creation.

        Covers:
            user.create_user
            user.get_all_users
            user.get_user
        """

        tid = api.team.create_team(self.base_team.copy())

        uids = []
        for i in range(users):
            name = "fred" + str(i)
            uids.append(api.user.create_user(
                name, name + "@gmail.com", name, tid
            ))

        assert len(set(uids)) == len(uids), "UIDs are not unique."

        assert len(api.user.get_all_users()) == users and \
            users == len(uids), "Not all users were created."

        for i, uid in enumerate(uids):
            name = "fred" + str(i)

            user_from_uid = api.user.get_user(uid=uid)
            user_from_name = api.user.get_user(name=name)

            assert user_from_uid == user_from_name, "User lookup from uid and name are not the same."

    @ensure_empty_collections("users", "teams")
    @clear_collections("users", "teams")
    def test_create_user_request_email_validation(self):
        """
        Tests the email validation during user registration.

        Covers:
            partially: user.create_user_request
        """

        team = self.base_team.copy()
        api.team.create_team(team)

        invalid_email_user = self.existing_team_user.copy()
        invalid_email_user["email"] = "not_an_email"

        with pytest.raises(WebException):
            api.user.create_user_request(invalid_email_user)
            assert False, "Was able to register a user with something that doesn't look like an email."

        invalid_email_user["email"] = "hax$@test.c"

        with pytest.raises(WebException):
            api.user.create_user_request(invalid_email_user)
            assert False, "Was able to register a user with invalid characters"

        valid_email_user = self.existing_team_user.copy()
        assert api.user.create_user_request(valid_email_user), "Was not able to register a valid email."

    @ensure_empty_collections("users", "teams")
    @clear_collections("users", "teams")
    def test_get_team(self):
        """
        Tests retrieving the team from a given uid.

        Covers:
            team.create_team
            user.create_user_request
            user.get_team
        """

        team = self.base_team.copy()
        tid = api.team.create_team(team)
        uid = api.user.create_user_request(self.existing_team_user.copy())

        result_team = api.user.get_team(uid=uid)
        assert tid == result_team['tid'], "Unable to pair uid and tid."

    @ensure_empty_collections("users", "teams")
    @clear_collections("users", "teams")
    def test_create_user_request_general_validation(self):
        """
        Tests the registration form validation functionality.

        Covers:
            partially: user.create_user_request
        """

        #Generally invalidate every length requirement
        for bad_length_mod in [0, 200]:
            for user_blueprint in [self.new_team_user, self.existing_team_user]:
                for key in user_blueprint.keys():
                    sheep_user = user_blueprint.copy()

                    #Make sure to keep the basic properties

                    if key == "create-new-team":
                        continue
                    elif key == "email":
                        sheep_user[key] = "x@x." + "x" * bad_length_mod
                    else:
                        sheep_user[key] = "A" * bad_length_mod

                    if sheep_user["create-new-team"] != "true" and \
                    safe_fail(api.team.get_team, name=sheep_user["team-name-existing"]) is None:
                        team = self.base_team.copy()
                        team['team_name'], team['password'] = \
                                sheep_user["team-name-existing"], sheep_user["team-password-existing"]
                        api.team.create_team(team)

                    with pytest.raises(WebException):
                        api.user.create_user_request(sheep_user)
                        assert False, "Validation failed to catch {} length {}".format(bad_length_mod, key)

    @ensure_empty_collections("users", "teams")
    @clear_collections("users", "teams")
    def test_create_user_request_new_team(self):
        """
        Tests the registration of users creating new teams.

        Covers:
            partially: user.create_user_request
            team.get_team_uids
        """

        uid = api.user.create_user_request(self.new_team_user)
        assert uid == api.user.get_user(name=self.new_team_user["username"])["uid"], "Good user created unsuccessfully."

        team = api.team.get_team(name=self.new_team_user["team-name-new"])
        assert team, "Team was not created."

        team_uids = api.team.get_team_uids(team["tid"])
        assert uid in team_uids, "User was not successfully placed into the new team."

        sheep_user = self.new_team_user.copy()
        sheep_user["username"] = "something_different"

        with pytest.raises(WebException):
            api.user.create_user_request(sheep_user)
            assert False, "Was able to create a new team... twice"

        sheep_user = self.new_team_user.copy()
        sheep_user["team-name-new"] = "noneixstent_team"

        with pytest.raises(WebException):
            api.user.create_user_request(sheep_user)
            assert False, "Was able to create two users with the same username."

    @ensure_empty_collections("users", "teams")
    @clear_collections("users", "teams")
    def test_create_user_request_existing_team(self):
        """
        Tests the registration of users on existing teams.

        Covers:
            partially: user.create_user_request
            team.get_team_uids
            team.create_team
        """

        tid = api.team.create_team(self.base_team.copy())
        assert tid, "Team was not created."

        uid = api.user.create_user_request(self.existing_team_user.copy())
        assert uid == api.user.get_user(name="valid")["uid"], "Good user created unsuccessfully."

        with pytest.raises(WebException):
            api.user.create_user_request(self.existing_team_user.copy())
            assert False, "Was able to register and join the team twice."

        with pytest.raises(WebException):
            invalid_team_user = self.existing_team_user.copy()
            invalid_team_user["team-name-existing"] = "Totally Invalid"
            api.user.create_user_request(invalid_team_user)
            assert False, "Was able to join a team that doesn't exist."

        with pytest.raises(WebException):
            invalid_team_user = self.existing_team_user.copy()
            invalid_team_user["team-password-existing"] = "Not correct"
            api.user.create_user_request(invalid_team_user)
            assert False, "Was able to join a team with an invalid password."

        team_uids = api.team.get_team_uids(tid)

        assert uid in team_uids, "User was not successfully placed into the existing team."
        assert len(team_uids) == 1, "Invalid teams were created though the tests passed."

    @ensure_empty_collections("users", "teams")
    @clear_collections("users", "teams")
    def test_change_password_user(self):
        """
        Tests password change functionality.

        Covers:
            user.update_password
            user.hash_password
        """

        tid = api.team.create_team(self.base_team.copy())
        uid = api.user.create_user("fred", "fred@gmail.com", "HASH", tid)

        old_hash = api.user.get_user(uid=uid)["password_hash"]
        assert old_hash == "HASH", "Was unable to confirm password was stored correctly."

        api.user.update_password_request({"password":"HACK", "confirm-password":"HACK"}, uid)

        new_hash = api.user.get_user(uid=uid)["password_hash"]

        assert bcrypt.hashpw("HACK", new_hash) == new_hash, \
            "Password does not match hashed plaintext after changing it."

        with pytest.raises(WebException):
            api.user.update_password_request({"password": "", "confirm-password":""}, uid)
            assert False, "Should not be able to update password to nothing."

    @ensure_empty_collections("users", "teams")
    @clear_collections("users", "teams")
    def test_create_teacher(self):
        """
        Tests teacher account creation.

        Covers: 
            user.create_user_request
            user.is_teacher
            user.get_all_users
        """

        teacher_uid = api.user.create_user_request(self.teacher_user.copy())


        eligible_uids = [u['uid'] for u in api.user.get_all_users()]
        all_uids = [u['uid'] for u in api.user.get_all_users(show_teachers=True)]

        assert api.user.is_teacher(uid=teacher_uid), "Teacher account is not flagged as teacher"
        assert teacher_uid not in eligible_uids, "Teacher was set to be eligible"
        assert teacher_uid in all_uids, "Teacher was not in list of all users"
