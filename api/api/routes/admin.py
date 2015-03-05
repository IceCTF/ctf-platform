from flask import Blueprint
import api

from api.common import WebSuccess, WebError
from api.annotations import api_wrapper, require_login, require_teacher, require_admin
from api.annotations import log_action

blueprint = Blueprint("admin_api", __name__)

@blueprint.route('/getallproblems', methods=['GET'])
@api_wrapper
@require_admin
def get_all_problems_hook():
    problems = api.problem.get_all_problems()
    if problems is None:
        return WebError("There was an error querying problems from the database.")
    return WebSuccess(data=problems)

@blueprint.route('/getallusers', methods=['GET'])
@api_wrapper
@require_admin
def get_all_users_hook():
    users = api.user.get_all_users()
    if users is None:
        return WebError("There was an error query users from the database.")
    return WebSuccess(data=users)
