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
import api.routes.group
import api.routes.problem
import api.routes.achievements

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
    app.register_blueprint(api.routes.group.blueprint, url_prefix="/api/group")
    app.register_blueprint(api.routes.problem.blueprint, url_prefix="/api/problems")
    app.register_blueprint(api.routes.achievements.blueprint, url_prefix="/api/achievements")

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

@app.route('/api/time', methods=['GET'])
@api_wrapper
def get_time():
    return WebSuccess(data=int(datetime.utcnow().timestamp()))
