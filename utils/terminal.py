import os
import colorama
import random

colorama.init()

colors = [
    colorama.Fore.WHITE,
    colorama.Fore.RED,
    colorama.Fore.GREEN,
    colorama.Fore.YELLOW,
    colorama.Fore.BLUE,
    colorama.Fore.MAGENTA,
    colorama.Fore.CYAN,
]

def print_bold(text):
    print(colorama.Style.BRIGHT + text + colorama.Style.RESET_ALL)

def _print_json(obj):
    output = ""
    for k,v in obj.items():
        output += f"{k}: {v}\n"
    
    return output

def _print_list(obj):
    output = ""
    for item in obj:
        if type(item) == dict:
            output += _print_json(item) + "\n"
        else:
            output += f"{item}\n"

    return output

def print_colored(text, color=None):
    if color:
        color = color.value
    else:
        color = random.randint(0, len(colors))

    if type(text) == dict:
        text = _print_json(text)

    if type(text) == list:
        text = _print_list(text)
    
    if text:
        print(colors[color] + text + colorama.Style.RESET_ALL)

def input_bold():
    return input(colorama.Style.BRIGHT + '> ' + colorama.Style.RESET_ALL)

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
