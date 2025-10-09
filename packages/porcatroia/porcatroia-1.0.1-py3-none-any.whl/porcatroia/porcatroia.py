import functools
import traceback
from colorama import Fore, Style, init
import random

init(autoreset=True)

RAINBOW = [
    Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA
]

def rainbow_textblock(text: str) -> str:
    lines = text.strip("\n").splitlines()
    result = []
    for i, line in enumerate(lines):
        color = RAINBOW[i % len(RAINBOW)]
        result.append(color + line)
    return "\n".join(result)

def porcatroia(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            try:
                art = """
__________________ ___________________     _____    _____________________ ________  .___   _____ ._.
\______   \_____  \\______   \_   ___ \   /  _  \   \__    ___/\______   \\_____  \ |   | /  _  \| |
 |     ___//   |   \|       _/    \  \/  /  /_\  \    |    |    |       _/ /   |   \|   |/  /_\  \ |
 |    |   /    |    \    |   \     \____/    |    \   |    |    |    |   \/    |    \   /    |    \|
 |____|   \_______  /____|_  /\______  /\____|__  /   |____|    |____|_  /\_______  /___\____|__  /_
                  \/       \/        \/         \/                     \/         \/            \/\/
                """
                print(rainbow_textblock(art))
                print(Fore.YELLOW + f"Non va una minchia nella funzione '{func.__name__}' ed ha tirato il bestemmione: ")
                print(Style.DIM)
                traceback.print_exc()
            except:
                pass

    return wrapper

