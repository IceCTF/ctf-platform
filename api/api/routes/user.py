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

blueprint = Blueprint("user_api", __name__)

@blueprint.route('/shell', methods=['GET'])
@api_wrapper
def get_shell_account_hook():
    if api.config.enable_shell:
        return WebSuccess(data=api.team.get_shell_account())
    return WebError(data="Shell is not available.")

@blueprint.route('/create', methods=['POST'])
@api_wrapper
def create_user_hook():
    new_uid = api.user.create_user_request(api.common.flat_multi(request.form))
    session['uid'] = new_uid
    return WebSuccess("User '{}' registered successfully!".format(request.form["username"]))

@blueprint.route('/update_password', methods=['POST'])
@api_wrapper
@check_csrf
@require_login
def update_password_hook():
    api.user.update_password_request(api.common.flat_multi(request.form), check_current=True)
    return WebSuccess("Your password has been successfully updated!")

@blueprint.route('/disable_account', methods=['POST'])
@api_wrapper
@check_csrf
@require_login
def disable_account_hook():
    api.user.disable_account_request(api.common.flat_multi(request.form), check_current=True)
    return WebSuccess("Your have successfully disabled your account!")

@blueprint.route('/reset_password', methods=['GET'])
@api_wrapper
def reset_password_hook():
    username = request.args.get("username", None)

    api.utilities.request_password_reset(username)
    return WebSuccess("A password reset link has been sent to the email address provided during registration.")

@blueprint.route('/confirm_password_reset', methods=['POST'])
@api_wrapper
def confirm_password_reset_hook():
    password = request.form.get("new-password")
    confirm = request.form.get("new-password-confirmation")
    token = request.form.get("reset-token")

    api.utilities.reset_password(token, password, confirm)
    return WebSuccess("Your password has been reset")

@blueprint.route('/login', methods=['POST'])
@api_wrapper
def login_hook():
    username = request.form.get('username')
    password = request.form.get('password')
    api.auth.login(username, password)
    return WebSuccess(message="Successfully logged in as " + username, data={'teacher': api.user.is_teacher()})

@blueprint.route('/logout', methods=['GET'])
@api_wrapper
def logout_hook():
    if api.auth.is_logged_in():
        api.auth.logout()
        return WebSuccess("Successfully logged out.")
    else:
        return WebError("You do not appear to be logged in.")

@blueprint.route('/status', methods=['GET'])
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
        "competition_active": api.utilities.check_competition_active(),
        "username": api.user.get_user()['username'] if api.auth.is_logged_in() else ""
    }

    return WebSuccess(data=status)
