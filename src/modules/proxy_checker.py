import os
import sys
import time
import asyncio
import aiohttp
from colorama import Fore, Style
from datetime import datetime
from rich.console import Console
from aiohttp_socks import ProxyConnector
from ..config.banners import PROXY_CHECKER_BANNER

class RushProxyChecker:
    def __init__(self, config):
        self.config = config
        self.console = Console()
        self.valid_proxies = []
        self.proxy_details = []
        self.timeout = aiohttp.ClientTimeout(total=10)
        self.total_proxies = 0
        self.alive_count = 0
        self.dead_count = 0
        self.speed = 0
        self.check_urls = [
            'https://google.com',
            'https://example.com',
            'https://cloudflare.com'
        ]
        self.stats = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'fastest': float('inf'),
            'slowest': 0,
            'average_speed': 0
        }

    async def check_proxy_async(self, proxy: str, protocol: str) -> dict:
        try:
            if protocol in ['http', 'https']:
                connector = aiohttp.TCPConnector(ssl=False)
                proxy_url = f'{protocol}://{proxy}'
            else:
                connector = ProxyConnector.from_url(f'{protocol}://{proxy}')
                proxy_url = None

            speeds = []
            successful_checks = 0

            for url in self.check_urls:
                try:
                    start_time = time.time()
                    async with aiohttp.ClientSession(connector=connector, timeout=self.timeout) as session:
                        async with session.get(url, proxy=proxy_url) as response:
                            if response.status == 200:
                                speed = time.time() - start_time
                                speeds.append(speed)
                                successful_checks += 1
                except:
                    continue

            if speeds:
                avg_speed = sum(speeds) / len(speeds)
                reliability = (successful_checks / len(self.check_urls)) * 100
                
                self.update_stats(avg_speed)
                
                return {
                    'proxy': proxy,
                    'speed': f'{avg_speed:.2f}s',
                    'protocol': protocol,
                    'alive': True,
                    'reliability': f'{reliability:.0f}%'
                }
        except:
            return None

    def update_stats(self, speed):
        self.stats['valid'] += 1
        self.stats['fastest'] = min(self.stats['fastest'], speed)
        self.stats['slowest'] = max(self.stats['slowest'], speed)
        self.stats['average_speed'] = (
            (self.stats['average_speed'] * (self.stats['valid'] - 1) + speed) / 
            self.stats['valid']
        )

    async def check_proxies_batch(self, proxies: list, protocol: str):
        tasks = []
        self.total_proxies = len(proxies)
        
        for proxy in proxies:
            task = asyncio.create_task(self.check_proxy_async(proxy.strip(), protocol))
            tasks.append(task)
        
        completed = 0
        for future in asyncio.as_completed(tasks):
            try:
                result = await future
                completed += 1
                
                if result:
                    self.alive_count += 1
                    self.valid_proxies.append(result['proxy'])
                    self.proxy_details.append(result)
                    self.speed = float(result['speed'].replace('s', ''))
                else:
                    self.dead_count += 1
                
                if completed < self.total_proxies:
                    self.display_progress(protocol, completed)
            except:
                self.dead_count += 1
                completed += 1
                if completed < self.total_proxies:
                    self.display_progress(protocol, completed)
        
        self.display_progress(protocol, self.total_proxies)

    def display_progress(self, protocol, completed):
        percentage = (completed / self.total_proxies) * 100
        bars = '█' * int(percentage / 2) + '░' * (50 - int(percentage / 2))
        
        print('\033[K', end='')
        print(f'\r{Fore.CYAN}[{bars}] {percentage:.1f}% | '
              f'{Fore.GREEN}Alive: {self.alive_count} | '
              f'{Fore.RED}Dead: {self.dead_count} | '
              f'{Fore.YELLOW}Speed: {self.speed:.2f}s | '
              f'{Fore.WHITE}Protocol: {protocol}', end='')

    def save_results(self, protocol: str):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = 'results/checked_proxies'
        os.makedirs(results_dir, exist_ok=True)
        
        filename = f'{results_dir}/valid_{protocol}_{timestamp}.txt'
        with open(filename, 'w') as f:
            f.write('\n'.join(self.valid_proxies))

        details_filename = f'{results_dir}/detailed_{protocol}_{timestamp}.txt'
        with open(details_filename, 'w') as f:
            f.write("=== PROXY CHECK RESULTS ===\n")
            f.write(f"Total Proxies: {self.stats['total']}\n")
            f.write(f"Valid Proxies: {self.stats['valid']}\n")
            f.write(f"Invalid Proxies: {self.stats['invalid']}\n")
            f.write(f"Average Speed: {self.stats['average_speed']:.2f}s\n")
            f.write(f"Fastest Proxy: {self.stats['fastest']:.2f}s\n")
            f.write(f"Slowest Proxy: {self.stats['slowest']:.2f}s\n\n")

            sorted_proxies = sorted(self.proxy_details, key=lambda x: float(x['speed'].replace('s', '')))
            
            f.write("=== ELITE PROXIES (< 1s) ===\n")
            for proxy in sorted_proxies:
                speed = float(proxy['speed'].replace('s', ''))
                if speed < 1:
                    f.write(f"{proxy['proxy']} | Speed: {proxy['speed']} | Reliability: {proxy['reliability']}\n")
            
            f.write("\n=== GOOD PROXIES (1-3s) ===\n")
            for proxy in sorted_proxies:
                speed = float(proxy['speed'].replace('s', ''))
                if 1 <= speed <= 3:
                    f.write(f"{proxy['proxy']} | Speed: {proxy['speed']} | Reliability: {proxy['reliability']}\n")
            
            f.write("\n=== AVERAGE PROXIES (>3s) ===\n")
            for proxy in sorted_proxies:
                speed = float(proxy['speed'].replace('s', ''))
                if speed > 3:
                    f.write(f"{proxy['proxy']} | Speed: {proxy['speed']} | Reliability: {proxy['reliability']}\n")

        print(f"\n{Fore.GREEN}[+] Results saved to:")
        print(f"{Fore.WHITE}    - {filename}")
        print(f"{Fore.WHITE}    - {details_filename}")

    async def start(self):
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(PROXY_CHECKER_BANNER)
            
            print(f"\n{Fore.CYAN}Select proxy type to check:")
            print(f"{Fore.WHITE}1. HTTP")
            print(f"{Fore.WHITE}2. HTTPS")
            print(f"{Fore.WHITE}3. SOCKS4")
            print(f"{Fore.WHITE}4. SOCKS5")
            
            choice = input(f"\n{Fore.YELLOW}Enter your choice (1-4): {Style.RESET_ALL}")
            proxy_types = {'1': 'http', '2': 'https', '3': 'socks4', '4': 'socks5'}
            protocol = proxy_types.get(choice)

            if not protocol:
                print(f"{Fore.RED}[!] Invalid choice!")
                return

            filepath = input(f"{Fore.YELLOW}Enter proxy file path: {Style.RESET_ALL}")
            
            with open(filepath, 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]

            self.stats['total'] = len(proxies)
            print(f"\n{Fore.CYAN}[*] Loaded {len(proxies)} proxies")
            print(f"{Fore.CYAN}[*] Starting proxy check...")
            
            await self.check_proxies_batch(proxies, protocol)

            self.stats['invalid'] = self.stats['total'] - self.stats['valid']
            
            print(f"\n{Fore.CYAN}═══ Check Complete ═══")
            print(f"{Fore.GREEN}Valid Proxies: {self.stats['valid']}")
            print(f"{Fore.RED}Invalid Proxies: {self.stats['invalid']}")
            print(f"{Fore.YELLOW}Average Speed: {self.stats['average_speed']:.2f}s")
            
            self.save_results(protocol)

        except FileNotFoundError:
            print(f"{Fore.RED}[!] Proxy file not found!")
        except Exception as e:
            print(f"{Fore.RED}[!] An error occurred: {str(e)}")
        finally:
            print(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            input()
