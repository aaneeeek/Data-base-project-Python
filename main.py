from DB_commands import DBMS
from colorama import Fore

if __name__ == "__main__":
    dbms = DBMS()
    while True:
        command: str = input(Fore.LIGHTYELLOW_EX + "Type in VinaSQL command: ")
        dbms.collect_commands(command)

