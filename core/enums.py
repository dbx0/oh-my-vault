from enum import Enum
class COLORS(Enum):
    WHITE = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6

class DEFAULTACTIONS(Enum):
    NEXTSTEP = "Continues to the next step"
    QUIT = "Quits the program"

class TARGETACTIONS(Enum):
    SCAN = "Use Shodan to find open OMV"
    UPLOADHOSTS = "Use a file to get a list of targets"
    UPLOADHOSTSWITHCREDENTIALS = "Use a file with targets and credentials"
    SINGLETARGET = "Input manually a target"

class AUTHACTIONS(Enum):
    BRUTEFORCE = "Bruteforce credentials"
    TESTDEFAULT = "Test for default credentials"
    USEEXISTING = "Use pre existing credentials on targets"
    RUN = "Start testing"

class ATTACKACTIONS(Enum):
    GETSYSTEMINFO = "Gets details about the host machine"
    ENUMERATEUSERS = "List all users in the host machine"
    ENUMERATESHAREDFOLDERS = "List all shared folders in OMV"
    RUNCOMMAND = "Executes a shell line in the target machine"
    REVSHELL = "Stars a reverse shell"

class STEP(Enum):
    ADDHOSTS = 1
    EXPLOIT = 2

class OMVDEFAULTCREDS(Enum):
    USERNAME = "admin"
    PASSWORD = "openmediavault"