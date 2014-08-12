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
        
        if db.ssh.count() >= api.config.shell_max_accounts:
            raise SevereInternalException("Max SSH accounts already created!")
        
        free_account_count = db.ssh.find({"tid": {"$exists": False}}).count()

        new_accounts = api.config.shell_free_acounts - free_account_count

        print("Adding {} new accounts...".format(new_accounts))

        while new_accounts > 0:
            username = random.choice(api.config.shell_user_prefixes) + \
                    str(random.randint(0, api.config.shell_max_accounts))

            plaintext_password = api.common.token()[:api.config.shell_password_length]
            
            hashed_password = shell.run(["bash", "-c", "echo '{}' | openssl passwd -1 -stdin".format(plaintext_password)])
            hashed_password = hashed_password.output.decode("utf-8")
            
            shell_cmd = api.config.shell_user_creation.format(username=username, password=hashed_password)
            
            result = shell.run(shell_cmd.split())
            
            if result.return_code != 0:
                raise InternalException(result.stderr)
            
            print("\t{}:{}".format(username, plaintext_password))

            new_accounts -= 1

    except spur.ssh.ConnectionError:
        raise SevereInternalException("Could not connect to shell server.")

