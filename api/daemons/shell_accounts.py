import api
import spur
import pwd
import random

from api.common import InternalException, SevereInternalException

def run():

    db = api.common.get_conn()

    try:
        shell = spur.SshShell(
            hostname=api.config.shell_host,
            username=api.config.shell_username,
            password=api.config.shell_password,
            port=api.config.shell_port,
            missing_host_key=spur.ssh.MissingHostKey.accept
        )

        result = shell.run(["sudo", "useradd", "--help"])

        if result.return_code != 0:
            raise SevereInternalException("Unable to sudo useradd.")

        account_count = db.ssh.count()
        if account_count >= api.config.shell_max_accounts:
            raise SevereInternalException("Max SSH accounts already created!")

        free_account_count = db.ssh.find({"tid": {"$exists": False}}).count()

        new_accounts = api.config.shell_free_acounts - free_account_count

        print("Checking that all teams have been assigned accounts...")

        print("{}/{} shell accounts allocated adding {}...".format(free_account_count, account_count, new_accounts))
        tids = [team["tid"] for team in api.team.get_all_teams(show_ineligible=True) \
                if db.ssh.find({"tid": team["tid"]}).count() == 0]

        if len(tids) > 0:
            print("{} teams without accounts present! Adding these as well.".format(len(tids)))
            new_accounts += len(tids)

        accounts = []
        while new_accounts > 0:
            username = random.choice(api.config.shell_user_prefixes) + \
                    str(random.randint(0, api.config.shell_max_accounts))

            plaintext_password = api.common.token()[:api.config.shell_password_length]

            hashed_password = shell.run(["bash", "-c", "echo '{}' | openssl passwd -1 -stdin".format(plaintext_password)])
            hashed_password = hashed_password.output.decode("utf-8")

            shell_cmd = api.config.shell_user_creation.format(username=username, password=hashed_password)

            result = shell.run(shell_cmd.split(), allow_error=True)

            if result.return_code == 9:
                print("Collision! Retrying.")
                continue
            elif result.return_code != 0:
                raise InternalException(result.stderr)

            print("\t{}:{}".format(username, plaintext_password))

            account = {
                "username": username,
                "password": plaintext_password,
                "hostname": api.config.shell_host,
                "port": api.config.shell_port
            }

            accounts.append(account)

            new_accounts -= 1

        if len(accounts) > 0:
            db.ssh.insert(accounts)
            print("Successfully imported accounts into mongo.")

        for tid in tids:
            api.team.assign_shell_account(tid=tid)

    except spur.ssh.ConnectionError:
        raise SevereInternalException("Could not connect to shell server.")
