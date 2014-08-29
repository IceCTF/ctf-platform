""" Module for utilities such as emailing, password reset, etc """

import smtplib
import bcrypt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

import api

from api.common import check, validate, safe_fail
from voluptuous import Required, Length, Schema
from datetime import datetime

enable_email = False
smtp_url = ''
email_username = ''
email_password = ''
from_addr = ''
from_name = ''

password_reset_request_schema = Schema({
    Required('username'): check(
        ("Usernames must be between 3 and 20 characters.", [str, Length(min=3, max=20)]),
    )
})

password_reset_schema = Schema({
    Required("token"): check(
        ("This does not look like a valid token.", [str, Length(max=100)])
    ),
    Required('password'): check(
        ("Passwords must be between 3 and 20 characters.", [str, Length(min=3, max=20)])
    )
})

def send_email(recipient, subject, body):
    """
    Send an email with the given body text and subject to the given recipient.

    Generates a MIMEMultipart message, connects to an smtp server using the credentials loaded from the configuration
    file, then sends the email.

    Args:
        recipient: the recipient of the email
        subject: the subject of the email
        body: the body of the email
    """

    #TODO: clean this up
    if enable_email:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = formataddr((from_name, from_addr))
        msg['To'] = recipient
        part1 = MIMEText(body, 'plain')
        msg.attach(part1)
        s = smtplib.SMTP_SSL(smtp_url)
        s.login(email_username, email_password)
        s.sendmail(from_addr, recipient, msg.as_string())
        s.quit()
    else:
        print("Emailing is disabled, not sending.")

def send_email_to_list(recipients, subject, body):
    """
    Sends an email to a list of recipients.

    If a list of recipients is passed we iterate over them and call send_email for each recipient.
    """

    if recipients is not None:
        for recipient in recipients:
            send_email(recipient, subject, body)

def reset_password(token, password, confirm_password):
    """
    Perform the password update operation.

    Gets a token and new password from a submitted form, if the token is found in a team object in the database
    the new password is hashed and set, the token is then removed and an appropriate response is returned.

    Args:
        token: the password reset token
        password: the password to set
        confirm_password: the same password again
    """

    validate(password_reset_schema, {"token": token, "password": password})
    user = api.user.find_user_by_reset_token(token)
    api.user.update_password_request({
            "new-password": password,
            "new-password-confirmation": confirm_password
    }, uid=user['uid'])

    api.user.delete_password_reset_token(user['uid'])

def request_password_reset(username):
    """
    Emails a user a link to reset their password.

    Checks that a username was submitted to the function and grabs the relevant team info from the db.
    Generates a secure token and inserts it into the team's document as 'password_reset_token'.
    A link is emailed to the registered email address with the random token in the url.  The user can go to this
    link to submit a new password, if the token submitted with the new password matches the db token the password
    is hashed and updated in the db.

    Args:
        username: the username of the account
    """

    validate(password_reset_request_schema, {"username":username})
    user = safe_fail(api.user.get_user, name=username)
    if user is None:
        raise WebException("No registration found for '{}'.".format(username))

    token = api.common.token()
    api.user.set_password_reset_token(user['uid'], token)

    msgBody = """We recently received a request to reset the password for the following {0} account:\n\n\t{2}\n\nOur records show that this is the email address used to register the above account.  If you did not request to reset the password for the above account then you need not take any further steps.  If you did request the password reset please follow the link below to set your new password. \n\n {1}/reset#{3} \n\n Best of luck! \n\n ~The {0} Team
    """.format(api.config.competition_name, api.config.competition_urls[0], username, token)

    send_email(user['email'], "{} Password Reset".format(api.config.competition_name), msgBody)

def check_competition_active():
    """
    Is the competition currently running
    """

    return api.config.start_time.timestamp() < datetime.utcnow().timestamp() < api.config.end_time.timestamp()

def load_news():
    """
    Get news to populate the news page.

    Queries the database for all news articles, loads them into a json document and returns them ordered by their date.
    Newest articles are at the beginning of the list to appear at the top of the news page.
    """

    db = api.common.get_conn()
    news = cache.get('news')
    if news is not None:
        return json.loads(news)
    news = sorted([{'date': str(n['date']) if 'date' in n else "2000-01-01",
                    'header': n['header'] if 'header' in n else None,
                    'articlehtml': n['articlehtml' if 'articlehtml' in n else None]}
                   for n in list(db.news.find())], key=lambda k: k['date'], reverse=True)
    cache.set('news', json.dumps(news), 60 * 2)
    return news
