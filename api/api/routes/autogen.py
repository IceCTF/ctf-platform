from flask import Flask, request, session, send_from_directory, render_template
from flask import Blueprint
import api
import json
import mimetypes
import os.path

from datetime import datetime
from api.common import WebSuccess, WebError
from api.annotations import api_wrapper, require_login, require_teacher, require_admin, check_csrf
from api.annotations import block_before_competition, block_after_competition
from api.annotations import log_action

blueprint = Blueprint("autogen_api", __name__)

def guess_mimetype(resource_path):
    """
    Guesses the mimetype of a given resource.

    Args:
        resource_path: the path to a given resource.
    Returns:
        The mimetype string.
    """

    mime = mimetypes.guess_type(resource_path)[0]

    if mime is None:
        return "application/octet-stream"

    return mime

@blueprint.route('/serve/<path>')
@require_login
def serve_autogen_hook(path):
    pid = request.args.get("pid", None)
    static = request.args.get("static", "false") == "true"

    tid = api.user.get_team()["tid"]

    if pid not in api.problem.get_unlocked_pids(tid):
        return WebError("You have not unlocked this problem!")

    instance_number = api.autogen.get_instance_number(pid, tid)

    if static:
        instance_path = api.autogen.get_static_instance_path(pid, public=True)
    else:
        instance_path = api.autogen.get_instance_path(pid, instance_number, public=True)

    mime = guess_mimetype(path)
    if mime == 'text/html':
        return send_from_directory(instance_path, path, mimetype=None, as_attachment=False, attachment_filename=None)
    else:
        return send_from_directory(instance_path, path, mimetype=mime)
