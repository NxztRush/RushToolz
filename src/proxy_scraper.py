import os
import sys
import time
import asyncio
import aiohttp
from colorama import Fore, Style
from datetime import datetime
from rich.console import Console
from aiohttp_socks import ProxyConnector

SCRAPER_BANNER = """
[Your RUSH SCRAPER ASCII art]
"""

class RushScraper:
    def __init__(self):
        self.console = Console()
        self.max_threads = 25
        self.proxies = set()
        self.valid_proxies = []
        self.proxy_details = []
        self.timeout = aiohttp.ClientTimeout(total=10)
        self.proxy_sources = {
            'http': [
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
                'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http',
                'https://www.proxy-list.download/api/v1/get?type=http',
                'https://api.openproxylist.xyz/http.txt',
                'https://raw.githubusercontent.com/shiftytr/proxy-list/master/proxy.txt',
                'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
                'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt',
                'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
                'https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt',
                'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt',
                'https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt',
                'https://www.proxyscan.io/download?type=http',
                'https://api.proxyscrape.com/?request=displayproxies&protocol=http',
                'https://openproxy.space/list/http',
                'https://proxyspace.pro/http.txt',
                'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt',
                'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps',
                'https://www.proxy-daily.com/api/getproxylist?apikey=free&protocol=http',
                'https://free-proxy-list.net/',
                'https://www.sslproxies.org/',
                'https://www.us-proxy.org/',
                'https://free-proxy-list.net/uk-proxy.html',
                'https://free-proxy-list.net/anonymous-proxy.html',
                'https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list',
                'https://raw.githubusercontent.com/scidam/proxy-list/master/proxy.json',
                'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt',
                'https://raw.githubusercontent.com/RX4096/proxy-list/main/online/http.txt',
                'https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt'
            ],
            'https': [
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/https.txt',
                'https://api.proxyscrape.com/v2/?request=getproxies&protocol=https',
                'https://www.proxy-list.download/api/v1/get?type=https',
                'https://api.openproxylist.xyz/https.txt',
                'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/https.txt',
                'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt',
                'https://www.proxyscan.io/download?type=https',
                'https://api.proxyscrape.com/?request=displayproxies&protocol=https',
                'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=https',
                'https://www.proxy-daily.com/api/getproxylist?apikey=free&protocol=https'
            ],
            'socks4': [
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
                'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4',
                'https://www.proxy-list.download/api/v1/get?type=socks4',
                'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt',
                'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt',
                'https://api.openproxylist.xyz/socks4.txt',
                'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt',
                'https://raw.githubusercontent.com/UserR3X/proxy-list/main/socks4.txt',
                'https://www.proxyscan.io/download?type=socks4',
                'https://api.proxyscrape.com/?request=displayproxies&protocol=socks4',
                'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks4',
                'https://www.proxy-daily.com/api/getproxylist?apikey=free&protocol=socks4',
                'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt',
                'https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks4.txt',
                'https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt',
                'https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/SOCKS4.txt',
                'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/socks4.txt',
                'https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks4.txt',
                'https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks4.txt',
                'https://raw.githubusercontent.com/prxchk/proxy-list/main/socks4.txt'
            ],
            'socks5': [
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
                'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5',
                'https://www.proxy-list.download/api/v1/get?type=socks5',
                'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt',
                'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt',
                'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt',
                'https://api.openproxylist.xyz/socks5.txt',
                'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt',
                'https://raw.githubusercontent.com/UserR3X/proxy-list/main/socks5.txt',
                'https://www.proxyscan.io/download?type=socks5',
                'https://api.proxyscrape.com/?request=displayproxies&protocol=socks5',
                'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5',
                'https://www.proxy-daily.com/api/getproxylist?apikey=free&protocol=socks5',
                'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt',
                'https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt',
                'https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt',
                'https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/SOCKS5.txt',
                'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/socks5.txt',
                'https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks5.txt',
                'https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks5.txt',
                'https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt',
                'https://raw.githubusercontent.com/hookzof/socks5_list/master/tg/socks.json'
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
            except:
                continue

    def display_progress(self, current, total, protocol):
        percentage = (current / total) * 100
        bars = '█' * int(percentage / 2) + '░' * (50 - int(percentage / 2))
        print(f'\r{Fore.CYAN}[{bars}] {Fore.GREEN}{percentage:.1f}% {Fore.WHITE}Checking {protocol} proxies...', end='')

    async def scrape_source_async(self, source: str) -> list:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(source, timeout=10) as response:
                    if response.status == 200:
                        text = await response.text()
                        return text.strip().split('\n')
        except:
            return []
        return []

    def save_results(self, protocol: str):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs('results', exist_ok=True)
        
        # Save valid proxies
        filename = f'results/valid_{protocol}_proxies_{timestamp}.txt'
        with open(filename, 'w') as f:
            f.write('\n'.join(self.valid_proxies))

        # Save detailed results
        details_filename = f'results/proxy_details_{protocol}_{timestamp}.txt'
        with open(details_filename, 'w') as f:
            for detail in self.proxy_details:
                f.write(f"Proxy: {detail['proxy']}\n")
                f.write(f"Speed: {detail['speed']}\n")
                f.write(f"Protocol: {detail['protocol']}\n")
                f.write("=" * 50 + "\n")

        print(f"\n{Fore.GREEN}[+] Results saved to:")
        print(f"{Fore.WHITE}    - {filename}")
        print(f"{Fore.WHITE}    - {details_filename}")

    def start(self):
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

        try:
            limit = int(input(f"{Fore.YELLOW}Enter proxy limit (max 25000): {Style.RESET_ALL}"))
            limit = min(limit, 25000)

            print(f"\n{Fore.CYAN}[*] Scraping {protocol.upper()} proxies...")
            asyncio.run(self.scrape_proxies_async(protocol, limit))
            
            print(f"\n{Fore.CYAN}[*] Checking proxies...")
            batch_size = self.max_threads
            proxy_list = list(self.proxies)
            
            for i in range(0, len(proxy_list), batch_size):
                batch = proxy_list[i:i + batch_size]
                asyncio.run(self.check_proxies_batch(batch, protocol))

            self.save_results(protocol)

        except ValueError:
            print(f"{Fore.RED}[!] Please enter a valid number!")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    async def scrape_proxies_async(self, protocol: str, limit: int):
        print(f"\n{Fore.YELLOW}[*] Scraping {protocol.upper()} proxies from {len(self.proxy_sources[protocol])} sources...")
        tasks = []
        for source in self.proxy_sources[protocol]:
            task = asyncio.create_task(self.scrape_source_async(source))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        for proxy_list in results:
            self.proxies.update(proxy_list)
        
        self.proxies = set(list(self.proxies)[:limit])
        print(f"{Fore.GREEN}[+] Found {len(self.proxies)} proxies!")
