import os
import sys
import time
import asyncio
import aiohttp
from colorama import Fore, Style
from datetime import datetime
from rich.console import Console
from aiohttp_socks import ProxyConnector
from ..config.banners import SCRAPER_BANNER

class RushScraper:
    def __init__(self, config):
        self.config = config
        self.console = Console()
        self.proxies = set()
        self.valid_proxies = []
        self.proxy_details = []
        self.timeout = aiohttp.ClientTimeout(total=10)
        self.proxy_sources = {
            'http': [
                'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http',
                'https://www.proxy-list.download/api/v1/get?type=http',
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
                'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
                'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt'
            ],
            'https': [
                'https://api.proxyscrape.com/v2/?request=getproxies&protocol=https',
                'https://www.proxy-list.download/api/v1/get?type=https',
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/https.txt',
                'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt',
                'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/https.txt'
            ],
            'socks4': [
                'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4',
                'https://www.proxy-list.download/api/v1/get?type=socks4',
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
                'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt',
                'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt'
            ],
            'socks5': [
                'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5',
                'https://www.proxy-list.download/api/v1/get?type=socks5',
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
                'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt',
                'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt'
            ]
        }

    async def check_proxy_async(self, proxy: str, protocol: str) -> dict:
        try:
            if protocol in ['http', 'https']:
                connector = aiohttp.TCPConnector(ssl=False)
                proxy_url = f'{protocol}://{proxy}'
            else:
                connector = ProxyConnector.from_url(f'{protocol}://{proxy}')
                proxy_url = None

            start_time = time.time()
            async with aiohttp.ClientSession(connector=connector, timeout=self.timeout) as session:
                async with session.get('https://www.google.com', proxy=proxy_url) as response:
                    if response.status == 200:
                        speed = time.time() - start_time
                        return {
                            'proxy': proxy,
                            'speed': f'{speed:.2f}s',
                            'protocol': protocol,
                            'alive': True
                        }
        except:
            return None

    async def check_proxies_batch(self, proxies: list, protocol: str):
        tasks = []
        for proxy in proxies:
            task = asyncio.create_task(self.check_proxy_async(proxy.strip(), protocol))
            tasks.append(task)
        
        total = len(proxies)
        for i, future in enumerate(asyncio.as_completed(tasks), 1):
            try:
                result = await future
                if result:
                    self.valid_proxies.append(result['proxy'])
                    self.proxy_details.append(result)
                self.display_progress(i, total, protocol)
            except Exception as e:
                continue

    def display_progress(self, current, total, protocol):
        try:
            percentage = (current / total) * 100
            bars = '█' * int(percentage / 2) + '░' * (50 - int(percentage / 2))
            print(f'\r{Fore.CYAN}[{bars}] {Fore.GREEN}{percentage:.1f}% {Fore.WHITE}Checking {protocol} proxies...', end='')
        except Exception:
            pass

    async def scrape_source_async(self, source: str) -> list:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(source, timeout=10) as response:
                    if response.status == 200:
                        text = await response.text()
                        return [proxy.strip() for proxy in text.split('\n') if proxy.strip()]
        except Exception:
            return []
        return []

    def save_results(self, protocol: str):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = 'results/proxies'
        os.makedirs(results_dir, exist_ok=True)
        
        # Save valid proxies
        filename = f'{results_dir}/valid_{protocol}_proxies_{timestamp}.txt'
        with open(filename, 'w') as f:
            f.write('\n'.join(self.valid_proxies))

        # Save detailed results
        details_filename = f'{results_dir}/proxy_details_{protocol}_{timestamp}.txt'
        with open(details_filename, 'w') as f:
            sorted_details = sorted(self.proxy_details, key=lambda x: float(x['speed'].replace('s', '')))
            
            f.write(f"Total Proxies: {len(sorted_details)}\n")
            f.write(f"Protocol: {protocol.upper()}\n")
            f.write("=" * 50 + "\n\n")
            
            for detail in sorted_details:
                f.write(f"Proxy: {detail['proxy']}\n")
                f.write(f"Speed: {detail['speed']}\n")
                f.write("=" * 30 + "\n")

        print(f"\n{Fore.GREEN}[+] Results saved to:")
        print(f"{Fore.WHITE}    - {filename}")
        print(f"{Fore.WHITE}    - {details_filename}")

    async def start(self):
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(SCRAPER_BANNER)
            
            print(f"\n{Fore.CYAN}Select proxy type:")
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

            limit = min(int(input(f"{Fore.YELLOW}Enter proxy limit (max 25000): {Style.RESET_ALL}") or "25000"), 25000)

            print(f"\n{Fore.CYAN}[*] Scraping {protocol.upper()} proxies...")
            
            for source in self.proxy_sources[protocol]:
                try:
                    proxies = await self.scrape_source_async(source)
                    self.proxies.update(proxies)
                    print(f"{Fore.GREEN}[+] Scraped {len(proxies)} proxies from source")
                except Exception:
                    continue

            self.proxies = set(list(self.proxies)[:limit])
            print(f"\n{Fore.GREEN}[+] Total unique proxies found: {len(self.proxies)}")
            
            print(f"\n{Fore.CYAN}[*] Starting proxy check...")
            batch_size = 100  # Reduced batch size for stability
            proxy_list = list(self.proxies)
            
            for i in range(0, len(proxy_list), batch_size):
                batch = proxy_list[i:i + batch_size]
                await self.check_proxies_batch(batch, protocol)

            self.save_results(protocol)

        except Exception as e:
            print(f"\n{Fore.RED}[!] An error occurred: {str(e)}")
        finally:
            print(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            input()
