"""
CTF API Configuration File

Note this is just a python script. It does config things.
"""

import api
import datetime
import os
from urllib.parse import urlparse
import json

config = {}
with open(os.path.join(os.path.dirname(__file__), "config.json")) as f:
    config = json.loads(f.read())

import api.app

""" FLASK """

api.app.session_cookie_domain = "icec.tf"
api.app.session_cookie_path = "/"
api.app.session_cookie_name = "icectf"

# KEEP THIS SECRET
api.app.secret_key = config["secret"]

""" SECURITY """

api.common.allowed_protocols = ["https", "http"]
api.common.allowed_ports = [8080]

""" MONGO """
api.common.mongo_db_name = "ctf"
api.common.mongo_addr = "127.0.0.1"
api.common.mongo_port = 27017

""" TESTING """

testing_mongo_db_name = "ctf_test"
testing_mongo_addr = api.common.mongo_addr
testing_mongo_port = api.common.mongo_port

""" CTF SETTINGS """

enable_teachers = False
enable_feedback = True

competition_name = "IceCTF"
competition_urls = ["https://icec.tf/play"]

# Max users on any given team
api.team.max_team_users = 4

# Teams to display on scoreboard graph
api.stats.top_teams = 5

start_time = datetime.datetime(2015, 8, 10, 0, 0, 0)
# start_time = datetime.datetime(2000, 10, 27, 12, 13, 0)
end_time = datetime.datetime(2055, 11, 7, 23, 59, 59)
freeze_time = datetime.datetime(2015, 8, 23, 23, 59, 59)

# Root directory of all problem graders
api.problem.grader_base_path = "/srv/problems/graders"

""" ACHIEVEMENTS """

enable_achievements = True

api.achievement.processor_base_path = "/srv/problems/achievements"

""" SHELL SERVER """

enable_shell = True

shell_host = config["shell"]["host"]
shell_username = config["shell"]["username"]
shell_password = config["shell"]["password"]
shell_port = 22

shell_user_prefixes  = ["ctf-"]
shell_password_length = 6
shell_free_acounts = 10
shell_max_accounts = 9999

shell_user_creation = "sudo useradd -m {username} -p {password} -g ctf -b /home_users"

""" EMAIL (SMTP) """

api.utilities.enable_email = True
api.utilities.smtp_url = config["email"]["smtp"]
api.utilities.smtp_protocol = config["email"]["protocol"]
api.utilities.email_username = config["email"]["username"]
api.utilities.email_password = config["email"]["password"]
api.utilities.from_addr = config["email"]["from_addr"]
api.utilities.from_name = config["email"]["from_name"]

""" CAPTCHA """
enable_captcha = True
captcha_url = "https://www.google.com/recaptcha/api/siteverify"
reCAPTCHA_private_key = config["recaptcha_key"]


""" AUTOGENERATED PROBLEMS """

api.autogen.seed = config["autogen_seed"]

""" LOGGING """

# Will be emailed any severe internal exceptions!
# Requires email block to be setup.
api.logger.admin_emails = ["icectf@icec.tf"]
api.logger.critical_error_timeout = 600