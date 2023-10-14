from core.enums import COLORS
from utils.terminal import print_colored
import os
import re

def read_list_file(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = [line.strip() for line in file.readlines()]
            return lines
    except FileNotFoundError:
        print_colored("[!] Unable to find specified file!", COLORS.RED)
    except Exception as e:
        print_colored(f"[!] Error reading file! Error message: {e}", COLORS.RED)

def write_list_file(lines, folder_path, file_name):
    try:
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'w') as file:
            for line in lines:
                file.write(f"{line}\n")

    except Exception as e:
        print_colored(f"[!] Error saving file! Error message: {e}", COLORS.RED)

def read_credentials_file(file_path):
    try:
        pattern = re.compile(r'([^-\s]+)\s*-\s*([^:]+):(.+)')
        targets_with_credentials = []

        with open(file_path, 'r') as file:
            lines = [line.strip() for line in file.readlines()]

        for line in lines:
            match = pattern.match(line)
            if not match:
                print_colored(f"[!] Unable to parse line: {line}", COLORS.RED)
            else:
                host = match.group(1)
                username = match.group(2)
                password = match.group(3)
                targets_with_credentials.append({"host": host, "username": username, "password": password})

        return targets_with_credentials
    except FileNotFoundError:
        print_colored("[!] Unable to find specified file!", COLORS.RED)
    except Exception as e:
        print_colored(f"[!] Error reading file! Error message: {e}", COLORS.RED)

def write_credentials_file(creds, folder_path, file_name):
    try:
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'w') as file:
            for host, cred in creds.items():
                file.write(f"{host} - {cred['username']}:{cred['password']}\n")

    except Exception as e:
        print_colored(f"[!] Error saving file! Error message: {e}", COLORS.RED)