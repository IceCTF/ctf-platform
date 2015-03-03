"""
Flask routing
"""

from flask import Flask, request, session, send_from_directory, render_template
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__, static_path="/")
app.wsgi_app = ProxyFix(app.wsgi_app)

import api
import json
import mimetypes
import os.path

from datetime import datetime
from api.common import WebSuccess, WebError
from api.annotations import api_wrapper, require_login, require_teacher, require_admin, check_csrf
from api.annotations import block_before_competition, block_after_competition
from api.annotations import log_action

import api.routes.autogen
import api.routes.user
import api.routes.team
import api.routes.stats
import api.routes.admin

log = api.logger.use(__name__)

session_cookie_domain = "127.0.0.1"
session_cookie_path = "/"
session_cookie_name = "flask"

secret_key = ""

def config_app(*args, **kwargs):
    """
    Return the app object configured correctly.
    This needed to be done for gunicorn.
    """

    app.secret_key = secret_key
    app.config["SESSION_COOKIE_DOMAIN"] = session_cookie_domain
    app.config["SESSION_COOKIE_PATH"] = session_cookie_path
    app.config["SESSION_COOKIE_NAME"] = session_cookie_name

    app.register_blueprint(api.routes.autogen.blueprint, url_prefix="/api/autogen")
    app.register_blueprint(api.routes.user.blueprint, url_prefix="/api/user")
    app.register_blueprint(api.routes.team.blueprint, url_prefix="/api/team")
    app.register_blueprint(api.routes.stats.blueprint, url_prefix="/api/stats")
    app.register_blueprint(api.routes.admin.blueprint, url_prefix="/api/admin")

    api.logger.setup_logs({"verbose": 2})
    return app

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, *')
    response.headers.add('Cache-Control', 'no-cache')
    response.headers.add('Cache-Control', 'no-store')
    if api.auth.is_logged_in():
        if 'token' in session:
            response.set_cookie('token', session['token'])
        else:
            csrf_token = api.common.token()
            session['token'] = csrf_token
            response.set_cookie('token', csrf_token)

    # JB: This is a hack. We need a better solution
    if request.path[0:19] != "/api/autogen/serve/":
        response.mimetype = 'appication/json'
    return response

@app.route('/api/problems', methods=['GET'])
@api_wrapper
@require_login
@block_before_competition(WebError("The competition has not begun yet!"))
def get_unlocked_problems_hook():
    return WebSuccess(data=api.problem.get_unlocked_problems(api.user.get_user()['tid']))

@app.route('/api/problems/solved', methods=['GET'])
@api_wrapper
@require_login
@block_before_competition(WebError("The competition has not begun yet!"))
def get_solved_problems_hook():
    return WebSuccess(api.problem.get_solved_problems(api.user.get_user()['tid']))

@app.route('/api/problems/submit', methods=['POST'])
@api_wrapper
@check_csrf
@require_login
@block_before_competition(WebError("The competition has not begun yet!"))
@block_after_competition(WebError("The competition is over!"))
def submit_key_hook():
    user_account = api.user.get_user()
    tid = user_account['tid']
    uid = user_account['uid']
    pid = request.form.get('pid', '')
    key = request.form.get('key', '')
    ip = request.remote_addr

    result = api.problem.submit_key(tid, pid, key, uid, ip)

    if result['correct']:
        return WebSuccess(result['message'], result['points'])
    else:
        return WebError(result['message'], {'code': 'wrong'})

@app.route('/api/problems/<path:pid>', methods=['GET'])
@api_wrapper
@require_login
@block_before_competition(WebError("The competition has not begun yet!"))
@block_after_competition(WebError("The competition is over!"))
def get_single_problem_hook(pid):
    problem_info = api.problem.get_problem(pid, tid=api.user.get_user()['tid'])
    return WebSuccess(data=problem_info)

@app.route('/api/problems/feedback', methods=['POST'])
@api_wrapper
@check_csrf
@require_login
@block_before_competition(WebError("The competition has not begun yet!"))
def problem_feedback_hook():
    feedback = json.loads(request.form.get("feedback", ""))
    pid = request.form.get("pid", None)

    if feedback is None or pid is None:
        return WebError("Please supply a pid and feedback.")

    api.problem_feedback.add_problem_feedback(pid, api.auth.get_uid(), feedback)
    return WebSuccess("Your feedback has been accepted.")

@app.route('/api/problems/feedback/reviewed', methods=['GET'])
@api_wrapper
@require_login
@block_before_competition(WebError("The competition has not begun yet!"))
def problem_reviews_hook():
    return WebSuccess(data=api.problem_feedback.get_reviewed_pids())

@app.route("/api/problems/hint", methods=['GET'])
@api_wrapper
@require_login
@block_before_competition(WebError("The competition has not begun yet!"))
def request_problem_hint_hook():

    @log_action
    def hint(pid, source):
        return None

    source = request.args.get("source")
    pid = request.args.get("pid")

    if pid is None:
        return WebError("Please supply a pid.")
    if source is None:
        return WebError("You have to supply the source of the hint.")

    tid = api.user.get_team()["tid"]
    if pid not in api.problem.get_unlocked_pids(tid):
        return WebError("Your team hasn't unlocked this problem yet!")

    hint(pid, source)
    return WebSuccess("Hint noted.")

@app.route('/api/group/list')
@api_wrapper
@require_login
def get_group_list_hook():
    return WebSuccess(data=api.team.get_groups())

@app.route('/api/group', methods=['GET'])
@api_wrapper
@require_login
def get_group_hook():
    name = request.form.get("group-name")
    owner = request.form.get("group-owner")
    owner_uid = api.user.get_user(name=owner)["uid"]
    if not api.group.is_member_of_group(name=name, owner_uid=owner_uid):
        return WebError("You are not a member of this group.")
    return WebSuccess(data=api.group.get_group(name=request.form.get("group-name"), owner_uid=owner_uid))

@app.route('/api/group/member_information', methods=['GET'])
@api_wrapper
def get_memeber_information_hook(gid=None):
    gid = request.args.get("gid")
    if not api.group.is_owner_of_group(gid):
        return WebError("You do not own that group!")

    return WebSuccess(data=api.group.get_member_information(gid=gid))

@app.route('/api/group/score', methods=['GET'])
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

@app.route('/api/group/create', methods=['POST'])
@api_wrapper
@check_csrf
@require_teacher
def create_group_hook():
    gid = api.group.create_group_request(api.common.flat_multi(request.form))
    return WebSuccess("Successfully created group", gid)

@app.route('/api/group/join', methods=['POST'])
@api_wrapper
@check_csrf
@require_login
def join_group_hook():
    api.group.join_group_request(api.common.flat_multi(request.form))
    return WebSuccess("Successfully joined group")

@app.route('/api/group/leave', methods=['POST'])
@api_wrapper
@check_csrf
@require_login
def leave_group_hook():
    api.group.leave_group_request(api.common.flat_multi(request.form))
    return WebSuccess("Successfully left group")

@app.route('/api/group/delete', methods=['POST'])
@api_wrapper
@check_csrf
@require_teacher
def delete_group_hook():
    api.group.delete_group_request(api.common.flat_multi(request.form))
    return WebSuccess("Successfully deleted group")

@app.route('/api/achievements', methods=['GET'])
@require_login
@api_wrapper
def get_achievements_hook():
    tid = api.user.get_team()["tid"]
    achievements = api.achievement.get_earned_achievements_display(tid=tid)

    for achievement in achievements:
        achievement["timestamp"] = None  # JB : Hack to temporarily fix achievements timestamp problem

    return WebSuccess(data=achievements)

@app.route('/api/stats/scoreboard', methods=['GET'])
@api_wrapper
@block_before_competition(WebError("The competition has not begun yet!"))
def get_scoreboard_hook():
    result = {}
    result['public'] = api.stats.get_all_team_scores()
    result['groups'] = []

    if api.auth.is_logged_in():
        for group in api.team.get_groups():
            result['groups'].append({
                'gid': group['gid'],
                'name': group['name'],
                'scoreboard': api.stats.get_group_scores(gid=group['gid'])
            })

    return WebSuccess(data=result)

@app.route('/api/stats/top_teams/score_progression', methods=['GET'])
@api_wrapper
def get_top_teams_score_progressions_hook():
    return WebSuccess(data=api.stats.get_top_teams_score_progressions())

@app.route('/api/time', methods=['GET'])
@api_wrapper
def get_time():
    return WebSuccess(data=int(datetime.utcnow().timestamp()))
