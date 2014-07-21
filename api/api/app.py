from flask import Flask, url_for, request, session

app = Flask(__name__)

import api

from api.common import WebSuccess, WebError
from api.annotations import api_wrapper, require_login, require_admin


log = api.logger.use(__name__)

session_cookie_domain = "127.0.0.1"
session_cookie_path = "/"
session_cookie_name = "flask"

secret_key = ""

def run(*args, **kwargs):
    """
    Start the api with configured values.
    """

    app.secret_key = secret_key
    app.config["SESSION_COOKIE_DOMAIN"] = session_cookie_domain
    app.config["SESSION_COOKIE_PATH"] = session_cookie_path
    app.config["SESSION_COOKIE_NAME"] = session_cookie_name

    app.run(*args, **kwargs)

@app.after_request
def after_request(response):
    #if (request.headers.get('Origin', '') in
    #        ['http://picoctf.com',
    #         'http://www.picoctf.com']):
    #    response.headers.add('Access-Control-Allow-Origin',
    #                         request.headers['Origin'])
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


@app.route("/api/sitemap", methods=["GET"])
@api_wrapper
def site_map_hook():
    print("Building sitemap")
    links = []
    for rule in app.url_map._rules:
        if "GET" in rule.methods or "POST" in rule.methods:
            try:
                url = url_for(rule.endpoint)
                links.append(url)
            except Exception:
                pass
    return WebSuccess("This is a message.", links)

@app.route('/api/user/create', methods=['POST'])
@api_wrapper
def create_user_hook():
    api.user.create_user_request(api.common.flat_multi(request.form))
    return WebSuccess("User '{}' registered successfully!".format(request.form["username"]))

@app.route('/api/user/updatepassword', methods=['POST'])
@api_wrapper
@require_login
def update_password_hook():
    uid = api.user.get_user()["uid"]
    password = request.form.get("password")
    confirm = request.form.get("confirm")

    if password != confirm:
        return WebError("Your passwords do not match.")

    api.user.update_password(uid, password)
    return WebSuccess("Your password has been successfully updated!")

@app.route('/api/user/getsshacct', methods=['GET'])
@api_wrapper
@require_login
def get_ssh_account_hook():
    data = api.user.get_ssh_account(api.user.get_user()['uid'])
    return WebSuccess(data=data)

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

@app.route('/api/user/score', methods=['GET'])
@require_login
@api_wrapper
def get_user_score_hook():
    score = api.scoreboard.get_score(uid=api.user.get_user()['uid'])
    if score is not None:
        return WebSuccess(data={'score': score})
    return WebError("There was an error retrieving your score.")

@app.route('/api/user/isloggedin', methods=['GET'])
@api_wrapper
def is_logged_in_hook():
    if api.auth.is_logged_in():
        return WebSuccess("You are logged in.")
    else:
        return WebError("You are not logged in.")

@app.route('/api/user/isadmin', methods=['GET'])
@api_wrapper
def is_admin_hook():
    if api.auth.is_admin():
        return WebSuccess("You have admin permissions.")
    else:
        return WebError("You do not have admin permissions.")

@app.route('/api/team', methods=['GET'])
@api_wrapper
@require_login
def team_information_hook():
    return WebSuccess(data=api.team.get_team_information())

@app.route('/api/team/score', methods=['GET'])
@require_login
@api_wrapper
def get_team_score_hook():
    score = api.scoreboard.get_score(tid=api.user.get_user()['tid'])
    if score is not None:
        return WebSuccess(data={'score': score})
    return WebError("There was an error retrieving your score.")

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
@require_login
@api_wrapper
def get_unlocked_problems_hook():
    return WebSuccess(data=api.problem.get_unlocked_problems(api.user.get_user()['tid']))

@app.route('/api/problems/solved', methods=['GET'])
@require_login
@api_wrapper
def get_solved_problems_hook():
    return WebSuccess(api.problem.get_solved_problems(api.user.get_user()['tid']))

@app.route('/api/problems/submit', methods=['POST'])
@require_login
@api_wrapper
def submit_key_hook():
    user_account = api.user.get_user()
    tid = user_account['tid']
    pid = request.form.get('pid', '')
    key = request.form.get('key', '')

    result = api.problem.submit_key(tid, pid, key)
    
    if result['correct']:
        return WebSuccess(result['message'], result['points'])
    else:
        return WebError(result['message'])

@app.route('/api/problems/<path:pid>', methods=['GET'])
@require_login
@api_wrapper
def get_single_problem_hook(pid):
    problem_info = api.problem.get_problem(pid, tid=api.user.get_user()['tid'])
    return WebSuccess(data=problem_info)

@app.route('/api/news', methods=['GET'])
@api_wrapper
def load_news_hook():
    return utilities.load_news()

@app.route('/api/lookupteamname', methods=['POST'])
@api_wrapper
def lookup_team_names_hook():
    email = request.form.get('email', '')
    return utilities.lookup_team_names(email)

@app.route('/api/game/categorystats', methods=['GET'])
@api_wrapper
@require_login
def get_category_statistics_hook():
    return api.game.get_category_statistics()

@app.route('/api/game/solvedindices', methods=['GET'])
@api_wrapper
@require_login
def get_solved_indices_hook():
    return api.game.get_solved_indices()

@app.route('/api/game/getproblem/<path:etcid>', methods=['GET'])
@api_wrapper
@require_login
def get_game_problem_hook(etcid):
    return api.game.get_game_problem(etcid)

@app.route('/api/game/to_pid/<path:etcid>', methods=['GET'])
@api_wrapper
@require_login
def etcid_to_pid_hook(etcid):
    return api.game.etcid_to_pid(etcid)

@app.route('/api/game/get_state', methods=['GET'])
@api_wrapper
@require_login
def get_state_hook():
    return api.game.get_state()

@app.route('/api/game/update_state', methods=['POST'])
@api_wrapper
@require_login
def update_state_hook():
    return api.game.update_state(request.form.get('avatar'),request.form.get('eventid'),
            request.form.get('level'))

@app.route('/api/group', methods=['GET'])
@api_wrapper
@require_login
def group_hook():
    groups = api.team.get_groups()
    return WebSuccess("Successfully retrieved the team's groups", groups)

@app.route('/api/group/score', methods=['GET'])
@require_login
@api_wrapper
def get_group_score_hook():
    score = api.scoreboard.get_group_score(name=request.form.get("group-name"))
    if score is not None:
        return WebSuccess(data={'score': score})
    return WebError("There was an error retrieving your score.")

@app.route('/api/group/create', methods=['POST'])
@api_wrapper
@require_login
def create_group_hook():
    gid = api.group.create_group_request(api.common.flat_multi(request.form))
    return WebSuccess("Successfully created group", gid)

@app.route('/api/group/join', methods=['POST'])
@api_wrapper
@require_login
def join_group_hook():
    api.group.join_group_request(api.common.flat_multi(request.form))
    return WebSuccess("Successfully joined group")

@app.route('/api/group/leave', methods=['POST'])
@api_wrapper
@require_login
def leave_group_hook():
    api.group.leave_group_request(api.common.flat_multi(request.form))
    return WebSuccess("Successfully left group")

@app.route('/api/group/delete', methods=['POST'])
@api_wrapper
@require_login
def delete_group_hook():
    api.group.delete_group_request(api.common.flat_multi(request.form))
    return WebSuccess("Successfully deleted group")

@app.route('/api/scoreboard', methods=['GET'])
@api_wrapper
def get_scoreboard_hook():
    result = {}
    result['public'] = api.scoreboard.get_all_team_scores()
    result['groups'] = []

    if api.auth.is_logged_in():
        for group in api.team.get_groups():
            result['groups'].append({
                'gid': group['gid'],
                'name': group['name'],
                'scoreboard': api.scoreboard.get_group_scores(gid=group['gid'])
            })

    return WebSuccess(data=result)
