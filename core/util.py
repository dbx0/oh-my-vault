import os

def print_data(dict_data):
    if type(dict_data) != list:
        dict_data = [dict_data]

    for row in dict_data:
        if row:
            for k,v in row.items():
                print(f"[*] {k}: {v}")

        print("")

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


