"""
Flask routing
"""

from flask import Flask, request, session, send_from_directory

app = Flask(__name__, static_path="/")

import api
import json

from api.common import WebSuccess, WebError
from api.annotations import api_wrapper, require_login, require_teacher, require_admin, check_csrf
from api.annotations import block_before_competition, block_after_competition

log = api.logger.use(__name__)

session_cookie_domain = "127.0.0.1"
session_cookie_path = "/"
session_cookie_name = "flask"

secret_key = ""

@app.route('/api/autogen/static/serve')
@require_login
def serve_autogen_static_hook():
    pid = request.args.get("pid", None)
    path = request.args.get("path", None)
    instance_path = api.autogen.get_static_instance_path(pid, public=True)
    return send_from_directory(instance_path, path)

@app.route('/api/autogen/serve')
@require_login
def serve_autogen_hook():
    pid = request.args.get("pid", None)
    path = request.args.get("path", None)
    tid = api.user.get_team()["tid"]
    instance_number = api.autogen.get_instance_number(pid, tid)
    instance_path = api.autogen.get_instance_path(pid, instance_number, public=True)
    return send_from_directory(instance_path, path)

def config_app(*args, **kwargs):
    """
    Start the api with configured values.
    """

    app.secret_key = secret_key
    app.config["SESSION_COOKIE_DOMAIN"] = session_cookie_domain
    app.config["SESSION_COOKIE_PATH"] = session_cookie_path
    app.config["SESSION_COOKIE_NAME"] = session_cookie_name

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

    response.mimetype = 'application/json'
    return response

@app.route('/api/user/shell', methods=['GET'])
@api_wrapper
def get_shell_account_hook():
    return WebSuccess(data=api.team.get_shell_account())

@app.route('/api/user/create', methods=['POST'])
@api_wrapper
def create_user_hook():
    new_uid = api.user.create_user_request(api.common.flat_multi(request.form))
    session['uid'] = new_uid
    return WebSuccess("User '{}' registered successfully!".format(request.form["username"]))

@app.route('/api/user/update_password', methods=['POST'])
@api_wrapper
@check_csrf
@require_login
def update_password_hook():
    api.user.update_password_request(api.common.flat_multi(request.form), check_current=True)
    return WebSuccess("Your password has been successfully updated!")

@app.route('/api/user/reset_password', methods=['GET'])
@api_wrapper
def reset_password_hook():
    username = request.args.get("username", None)

    api.utilities.request_password_reset(username)
    return WebSuccess("A password reset link has been sent to the email address provided during registration.")

@app.route('/api/user/confirm_password_reset', methods=['POST'])
@api_wrapper
@check_csrf
def confirm_password_reset_hook():
    password = request.form.get("new-password")
    confirm = request.form.get("new-password-confirmation")
    token = request.form.get("reset-token")

    api.utilities.reset_password(token, password, confirm)
    return WebSuccess("Your password has been reset")

@app.route('/api/user/login', methods=['POST'])
@api_wrapper
def login_hook():
    username = request.form.get('username')
    password = request.form.get('password')
    api.auth.login(username, password)
    return WebSuccess("Successfully logged in as " + username)

@app.route('/api/user/logout', methods=['GET'])
@api_wrapper
def logout_hook():
    if api.auth.is_logged_in():
        api.auth.logout()
        return WebSuccess("Successfully logged out.")
    else:
        return WebError("You do not appear to be logged in.")

@app.route('/api/user/status', methods=['GET'])
@api_wrapper
def status_hook():
    status = {
        "logged_in": api.auth.is_logged_in(),
        "admin": api.auth.is_admin(),
        "teacher": api.auth.is_logged_in() and api.user.is_teacher(),
        "enable_teachers": api.config.enable_teachers,
        "enable_feedback": api.config.enable_feedback,
        "shell": api.config.enable_shell,
        "enable_captcha": api.config.enable_captcha,
        "competition_active": api.utilities.check_competition_active()
    }

    return WebSuccess(data=status)

@app.route('/api/team', methods=['GET'])
@api_wrapper
@require_login
def team_information_hook():
    return WebSuccess(data=api.team.get_team_information())

@app.route('/api/team/score', methods=['GET'])
@api_wrapper
@require_login
def get_team_score_hook():
    score = api.stats.get_score(tid=api.user.get_user()['tid'])
    if score is not None:
        return WebSuccess(data={'score': score})
    return WebError("There was an error retrieving your score.")

@app.route('/api/stats/team/solved_problems', methods=['GET'])
@api_wrapper
@require_login
@block_before_competition(WebError("The competition has not begun yet!"))
def get_team_solved_problems_hook():
    tid = request.args.get("tid", "")
    stats = {
        "problems": api.stats.get_problems_by_category(),
        "members": api.stats.get_team_member_stats(tid)
    }

    return WebSuccess(data=stats)

@app.route('/api/stats/team/score_progression', methods=['GET'])
@api_wrapper
@require_login
@block_before_competition(WebError("The competition has not begun yet!"))
def get_team_score_progression():
    category = request.form.get("category", None)

    tid = api.user.get_team()["tid"]

    return WebSuccess(data=[api.stats.get_score_progression(tid=tid, category=category)])

@app.route('/api/admin/getallproblems', methods=['GET'])
@api_wrapper
@require_admin
def get_all_problems_hook():
    problems = api.problem.get_all_problems()
    if probs is None:
        return WebError("There was an error querying problems from the database.")
    return WebSuccess(data=problems)

@app.route('/api/admin/getallusers', methods=['GET'])
@api_wrapper
@require_admin
def get_all_users_hook():
    users = api.user.get_all_users()
    if users is None:
        return WebError("There was an error query users from the database.")
    return WebSuccess(data=users)

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
        return WebError(result['message'])

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

@app.route('/api/game/categorystats', methods=['GET'])
@api_wrapper
@require_login
@block_before_competition(WebError("The competition has not begun yet!"))
@block_after_competition(WebError("The competition is over!"))
def get_category_statistics_hook():
    return api.game.get_category_statistics()

@app.route('/api/game/solvedindices', methods=['GET'])
@api_wrapper
@require_login
@block_before_competition(WebError("The competition has not begun yet!"))
@block_after_competition(WebError("The competition is over!"))
def get_solved_indices_hook():
    return api.game.get_solved_indices()

@app.route('/api/game/getproblem/<path:etcid>', methods=['GET'])
@api_wrapper
@require_login
@block_before_competition(WebError("The competition has not begun yet!"))
@block_after_competition(WebError("The competition is over!"))
def get_game_problem_hook(etcid):
    return api.game.get_game_problem(etcid)

@app.route('/api/game/to_pid/<path:etcid>', methods=['GET'])
@api_wrapper
@require_login
@block_before_competition(WebError("The competition has not begun yet!"))
@block_after_competition(WebError("The competition is over!"))
def etcid_to_pid_hook(etcid):
    return api.game.etcid_to_pid(etcid)

@app.route('/api/game/get_state', methods=['GET'])
@api_wrapper
@require_login
@block_before_competition(WebError("The competition has not begun yet!"))
@block_after_competition(WebError("The competition is over!"))
def get_state_hook():
    return api.game.get_state()

@app.route('/api/game/update_state', methods=['POST'])
@api_wrapper
@require_login
@block_before_competition(WebError("The competition has not begun yet!"))
@block_after_competition(WebError("The competition is over!"))
def update_state_hook():
    return api.game.update_state(request.form.get('avatar'),request.form.get('eventid'),
            request.form.get('level'))

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
    achievements = api.achievement.get_earned_achievements(tid=tid)

    for achievement in achievements:
        achievement["timestamp"] = achievement["timestamp"].timestamp()

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
