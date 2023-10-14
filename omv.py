#!/usr/bin/env python
import sys
sys.dont_write_bytecode = True

__import__("utils.versioncheck")

from utils.banner import print_banner
from core.enums import COLORS
from core import wizard
from utils.terminal import print_colored

def shutdown():
    print_colored("\n[!] Exiting...", COLORS.RED)
    exit()

try:

    if __name__ == "__main__":
        print_banner()
        wizard.run()

except KeyboardInterrupt:
    shutdown()
except Exception as e:
    print_colored(f"[!] Error: {e}", COLORS.RED)
    raise e

    