from flask import Flask, request, session, send_from_directory, render_template
from flask import Blueprint
import api

from api.common import WebSuccess, WebError
from api.annotations import api_wrapper, require_login, require_teacher, require_admin, check_csrf
from api.annotations import block_before_competition, block_after_competition
from api.annotations import log_action

blueprint = Blueprint("group_api", __name__, template_folder="templates")

@blueprint.route('', methods=['GET'])
@api_wrapper
@require_login
def get_group_hook():
    name = request.form.get("group-name")
    owner = request.form.get("group-owner")
    owner_uid = api.user.get_user(name=owner)["uid"]
    if not api.group.is_member_of_group(name=name, owner_uid=owner_uid):
        return WebError("You are not a member of this group.")
    return WebSuccess(data=api.group.get_group(name=request.form.get("group-name"), owner_uid=owner_uid))

@blueprint.route('/list')
@api_wrapper
@require_login
def get_group_list_hook():
    return WebSuccess(data=api.team.get_groups())

@blueprint.route('/member_information', methods=['GET'])
@api_wrapper
def get_memeber_information_hook(gid=None):
    gid = request.args.get("gid")
    if not api.group.is_owner_of_group(gid):
        return WebError("You do not own that group!")

    return WebSuccess(data=api.group.get_member_information(gid=gid))

@blueprint.route('/score', methods=['GET'])
@api_wrapper
@require_teacher
def get_group_score_hook():  #JB: Fix this
    name = request.args.get("group-name")
    if not api.group.is_owner_of_group(gid=name):
        return WebError("You do not own that group!")

    #TODO: Investigate!
    score = api.stats.get_group_scores(name=name)
    if score is None:
        return WebError("There was an error retrieving your score.")

    return WebSuccess(data={'score': score})

@blueprint.route('/create', methods=['POST'])
@api_wrapper
@check_csrf
@require_teacher
def create_group_hook():
    gid = api.group.create_group_request(api.common.flat_multi(request.form))
    return WebSuccess("Successfully created group", gid)

@blueprint.route('/join', methods=['POST'])
@api_wrapper
@check_csrf
@require_login
def join_group_hook():
    api.group.join_group_request(api.common.flat_multi(request.form))
    return WebSuccess("Successfully joined group")

@blueprint.route('/leave', methods=['POST'])
@api_wrapper
@check_csrf
@require_login
def leave_group_hook():
    api.group.leave_group_request(api.common.flat_multi(request.form))
    return WebSuccess("Successfully left group")

@blueprint.route('/delete', methods=['POST'])
@api_wrapper
@check_csrf
@require_teacher
def delete_group_hook():
    api.group.delete_group_request(api.common.flat_multi(request.form))
    return WebSuccess("Successfully deleted group")
