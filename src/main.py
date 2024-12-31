import os
from colorama import init, Fore, Style
from checker import RushChecker
from inboxer import RushInboxer
from proxy_scraper import RushScraper
from proxy_checker import RushProxyChecker

init()

MAIN_MENU_BANNER = """
\033[38;5;93m██████╗ ██╗   ██╗███████╗██╗  ██╗
\033[38;5;99m██╔══██╗██║   ██║██╔════╝██║  ██║
\033[38;5;105m██████╔╝██║   ██║███████╗███████║
\033[38;5;161m██╔══██╗██║   ██║╚════██║██╔══██║
\033[38;5;162m██║  ██║╚██████╔╝███████║██║  ██║
\033[38;5;196m╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
\033[38;5;51m████████╗ ██████╗  ██████╗ ██╗     ███████╗
\033[38;5;45m╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
\033[38;5;39m   ██║   ██║   ██║██║   ██║██║     ███████╗
\033[38;5;33m   ██║   ██║   ██║██║   ██║██║     ╚════██║
\033[38;5;27m   ██║   ╚██████╔╝╚██████╔╝███████╗███████║
\033[38;5;21m   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝\033[0m"""
PROXY_BANNER = """
\033[38;5;93m██████╗ ██╗   ██╗███████╗██╗  ██╗
\033[38;5;99m██╔══██╗██║   ██║██╔════╝██║  ██║
\033[38;5;105m██████╔╝██║   ██║███████╗███████║
\033[38;5;161m██╔══██╗██║   ██║╚════██║██╔══██║
\033[38;5;162m██║  ██║╚██████╔╝███████║██║  ██║
\033[38;5;196m╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
\033[38;5;51m████████╗ ██████╗  ██████╗ ██╗     ███████╗
\033[38;5;45m╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
\033[38;5;39m   ██║   ██║   ██║██║   ██║██║     ███████╗
\033[38;5;33m   ██║   ██║   ██║██║   ██║██║     ╚════██║
\033[38;5;27m   ██║   ╚██████╔╝╚██████╔╝███████╗███████║
\033[38;5;21m   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝\033[0m"""

PROXY_CHECKER_BANNER = """
\033[38;5;93m██████╗ ██╗   ██╗███████╗██╗  ██╗
\033[38;5;99m██╔══██╗██║   ██║██╔════╝██║  ██║
\033[38;5;105m██████╔╝██║   ██║███████╗███████║
\033[38;5;161m██╔══██╗██║   ██║╚════██║██╔══██║
\033[38;5;162m██║  ██║╚██████╔╝███████║██║  ██║
\033[38;5;196m╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
\033[38;5;51m████████╗ ██████╗  ██████╗ ██╗     ███████╗
\033[38;5;45m╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
\033[38;5;39m   ██║   ██║   ██║██║   ██║██║     ███████╗
\033[38;5;33m   ██║   ██║   ██║██║   ██║██║     ╚════██║
\033[38;5;27m   ██║   ╚██████╔╝╚██████╔╝███████╗███████║
\033[38;5;21m   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝\033[0m"""


def main_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(MAIN_MENU_BANNER)
        print(f"{Fore.MAGENTA}═══════════════════════════════════")
        print(f"{Fore.CYAN}1. HM Checker")
        print(f"{Fore.CYAN}2. HM Inboxer")
        print(f"{Fore.CYAN}3. Proxy Tools")
        print(f"{Fore.RED}4. Exit")
        print(f"{Fore.MAGENTA}═══════════════════════════════════")
        
        choice = input(f"\n{Fore.YELLOW}Choose an option: {Style.RESET_ALL}")
        
        if choice == "1":
            checker = RushChecker()
            checker.start()
        elif choice == "2":
            inboxer = RushInboxer()
            inboxer.start()
        elif choice == "3":
            proxy_menu()
        elif choice == "4":
            print(f"{Fore.GREEN}Thanks for using RUSH TOOLS!")
            break

def proxy_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(PROXY_BANNER)
        print(f"{Fore.MAGENTA}═══════════════════════════════════")
        print(f"{Fore.CYAN}1. Proxy Scraper")
        print(f"{Fore.CYAN}2. Proxy Checker")
        print(f"{Fore.RED}3. Back")
        print(f"{Fore.MAGENTA}═══════════════════════════════════")
        
        choice = input(f"\n{Fore.YELLOW}Choose an option: {Style.RESET_ALL}")
        
        if choice == "1":
            scraper = RushScraper()
            scraper.start()
        elif choice == "2":
            checker = RushProxyChecker()
            checker.start()
        elif choice == "3":
            break

if __name__ == "__main__":
    main_menu()
