"""
Manage loggers for the api.
"""

import logging
import api

from bson import json_util

from flask import request, has_request_context
from flask import logging as flask_logging

from sys import stdout
from datetime import datetime

log = logging.getLogger(__name__)

#TODO: Add configuration for this.
class StatsHandler(logging.StreamHandler):
    """
    Logs statistical information into the mongodb.
    """

    time_format = "%H:%M:%S %Y-%m-%d"

    action_parsers = {
        "api.user.create_user_request":
            lambda params, result=None: {
                "username": params["username"],
                "new_team": params["create-new-team"] == "on"
            }
    }

    def __init__(self):

        logging.StreamHandler.__init__(self)

    def emit(self, record):
        """
        Store record into the db.
        """

        information = get_request_information()

        result = record.msg

        if type(result) == dict:

            information.update({
                "event": result["name"],
                "time": datetime.now().strftime(self.time_format)
            })

            information["action"] = {
                "pass": True
            }

            if "exception" in result:
                information["action"].update({
                    "exception": result["exception"],
                    "pass": False
                })
            elif result["name"] in self.action_parsers:
                action_parser = self.action_parsers[result["name"]]

                result["kwargs"]["result"] = result["result"]
                action_result = action_parser(*result["args"], **result["kwargs"])

                information["action"].update(action_result)

            print(json_util.dumps(information, indent=4))
            api.common.get_conn().statistics.insert(information)

def set_level(name, level):
    """
    Get and set log level of a given logger.

    Args:
        name: name of logger
        level: level to set
    """

    logger = use(name)
    if logger:
        logger.setLevel(level)

def use(name):
    """
    Alias for logging.getLogger(name)

    Args:
        name: The name of the logger.
    Returns:
        The logging object.
    """

    return logging.getLogger(name)

def get_request_information():
    """
    Returns a dictionary of contextual information about the user at the time of logging.

    Returns:
        The dictionary.
    """

    information = {}

    if has_request_context():
        information["request"] = {
            "api_endpoint_method": request.method,
            "api_endpoint": request.path,
            "ip": request.remote_addr,
            "platform": request.user_agent.platform,
            "browser": request.user_agent.browser,
            "browser_version": request.user_agent.version,
            "user_agent":request.user_agent.string
        }

        if api.auth.is_logged_in():

            user = api.user.get_user()
            team = api.user.get_team()
            groups = api.team.get_groups()

            information["user"] = {
                "username": user["username"],
                "email": user["email"],
                "team_name": team["team_name"],
                "school": team["school"],
                "groups": [group["name"] for group in groups]
            }

    return information

def setup_logs(args):
    """
    Initialize the api loggers.

    Args:
        args: dict containing the configuration options.
    """

    flask_logging.create_logger = lambda app: use(app.logger_name)

    if not args['debug']:
        set_level("werkzeug", logging.ERROR)

    level = [logging.WARNING, logging.INFO, logging.DEBUG][
        min(args.get("verbose", 1), 2)]

    internal_error_log = logging.StreamHandler(stdout)
    internal_error_log.setLevel(logging.ERROR)

    severe_error_log = logging.StreamHandler(stdout)
    severe_error_log.setLevel(logging.CRITICAL)

    stats_log = StatsHandler()
    stats_log.setLevel(logging.INFO)

    log.root.setLevel(level)
    log.root.addHandler(internal_error_log)
    log.root.addHandler(severe_error_log)
    log.root.addHandler(stats_log)
