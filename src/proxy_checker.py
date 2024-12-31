import os
import sys
import time
import asyncio
import aiohttp
import logging
from colorama import Fore, Style, init
from datetime import datetime
from rich.console import Console
from aiohttp_socks import ProxyConnector
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='proxy_checker.log'
)

class ProxyCheckError(Exception):
    """Custom exception for proxy checking errors"""
    pass

class RushProxyChecker:
    def __init__(self, config=None):
        try:
            self.config = config or {}
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
            self.stats = self._initialize_stats()
            logging.info("RushProxyChecker initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize RushProxyChecker: {str(e)}")
            raise

    def _initialize_stats(self) -> Dict[str, Any]:
        return {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'fastest': float('inf'),
            'slowest': 0,
            'average_speed': 0,
            'errors': 0
        }

    async def check_proxy_async(self, proxy: str, protocol: str) -> Optional[Dict[str, Any]]:
        try:
            if not proxy or not protocol:
                raise ValueError("Invalid proxy or protocol")

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
                except aiohttp.ClientError as e:
                    logging.warning(f"Connection error for proxy {proxy}: {str(e)}")
                    continue
                except Exception as e:
                    logging.error(f"Unexpected error checking proxy {proxy}: {str(e)}")
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
            return None

        except Exception as e:
            logging.error(f"Error checking proxy {proxy}: {str(e)}")
            self.stats['errors'] += 1
            return None

    def update_stats(self, speed: float) -> None:
        try:
            self.stats['valid'] += 1
            self.stats['fastest'] = min(self.stats['fastest'], speed)
            self.stats['slowest'] = max(self.stats['slowest'], speed)
            self.stats['average_speed'] = (
                (self.stats['average_speed'] * (self.stats['valid'] - 1) + speed) / 
                self.stats['valid']
            )
        except Exception as e:
            logging.error(f"Error updating stats: {str(e)}")
            raise ProxyCheckError("Failed to update statistics")

    async def check_proxies_batch(self, proxies: list, protocol: str) -> None:
        try:
            tasks = []
            self.total_proxies = len(proxies)
            
            print("\n")
            self.display_progress(protocol, 0)
            
            for proxy in proxies:
                if not proxy.strip():
                    continue
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
                        print(f"\n{Fore.GREEN}[VALID] {result['proxy']} | Speed: {result['speed']} | Reliability: {result['reliability']}")
                    else:
                        self.dead_count += 1
                        print(f"\n{Fore.RED}[DEAD] Proxy check failed")
                    
                    self.display_progress(protocol, completed)
                except asyncio.CancelledError:
                    logging.warning("Task cancelled")
                    break
                except Exception as e:
                    logging.error(f"Error processing proxy result: {str(e)}")
                    self.dead_count += 1
                    completed += 1
                    self.display_progress(protocol, completed)

        except Exception as e:
            logging.error(f"Batch check failed: {str(e)}")
            raise ProxyCheckError("Failed to complete proxy batch check")

    def display_progress(self, protocol: str, completed: int) -> None:
        try:
            percentage = (completed / self.total_proxies) * 100
            bars = '█' * int(percentage / 2) + '░' * (50 - int(percentage / 2))
            
            sys.stdout.write("\033[F")
            sys.stdout.write("\033[K")
            
            print(f'{Fore.CYAN}[{bars}] {percentage:.1f}% | '
                  f'{Fore.GREEN}Alive: {self.alive_count} | '
                  f'{Fore.RED}Dead: {self.dead_count} | '
                  f'{Fore.YELLOW}Speed: {self.speed:.2f}s | '
                  f'{Fore.WHITE}Protocol: {protocol}')
        except Exception as e:
            logging.error(f"Error displaying progress: {str(e)}")

    def save_results(self, protocol: str) -> None:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_dir = 'results/checked_proxies'
            os.makedirs(results_dir, exist_ok=True)
            
            filename = f'{results_dir}/valid_{protocol}_{timestamp}.txt'
            details_filename = f'{results_dir}/detailed_{protocol}_{timestamp}.txt'

            with open(filename, 'w') as f:
                f.write('\n'.join(self.valid_proxies))

            with open(details_filename, 'w') as f:
                self._write_detailed_results(f)

            print(f"\n{Fore.GREEN}[+] Results saved to:")
            print(f"{Fore.WHITE}    - {filename}")
            print(f"{Fore.WHITE}    - {details_filename}")
            
            logging.info(f"Results saved successfully to {filename} and {details_filename}")

        except IOError as e:
            logging.error(f"Failed to save results: {str(e)}")
            raise ProxyCheckError("Failed to save proxy check results")

    def _write_detailed_results(self, file_handle) -> None:
        try:
            file_handle.write("=== PROXY CHECK RESULTS ===\n")
            file_handle.write(f"Total Proxies: {self.stats['total']}\n")
            file_handle.write(f"Valid Proxies: {self.stats['valid']}\n")
            file_handle.write(f"Invalid Proxies: {self.stats['invalid']}\n")
            file_handle.write(f"Average Speed: {self.stats['average_speed']:.2f}s\n")
            file_handle.write(f"Fastest Proxy: {self.stats['fastest']:.2f}s\n")
            file_handle.write(f"Slowest Proxy: {self.stats['slowest']:.2f}s\n")
            file_handle.write(f"Errors Encountered: {self.stats['errors']}\n\n")

            sorted_proxies = sorted(self.proxy_details, key=lambda x: float(x['speed'].replace('s', '')))
            
            for category, speed_range in [
                ("ELITE PROXIES (< 1s)", lambda s: s < 1),
                ("GOOD PROXIES (1-3s)", lambda s: 1 <= s <= 3),
                ("AVERAGE PROXIES (>3s)", lambda s: s > 3)
            ]:
                file_handle.write(f"=== {category} ===\n")
                for proxy in sorted_proxies:
                    speed = float(proxy['speed'].replace('s', ''))
                    if speed_range(speed):
                        file_handle.write(f"{proxy['proxy']} | Speed: {proxy['speed']} | Reliability: {proxy['reliability']}\n")
                file_handle.write("\n")

        except Exception as e:
            logging.error(f"Error writing detailed results: {str(e)}")
            raise ProxyCheckError("Failed to write detailed results")

    async def start(self) -> None:
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(PROXY_CHECKER_BANNER)
            
            protocol = self._get_protocol_choice()
            if not protocol:
                return

            filepath = input(f"{Fore.YELLOW}Enter proxy file path: {Style.RESET_ALL}")
            
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Proxy file not found: {filepath}")

            proxies = self._load_proxies(filepath)
            if not proxies:
                raise ValueError("No valid proxies found in file")

            self.stats['total'] = len(proxies)
            print(f"\n{Fore.CYAN}[*] Loaded {len(proxies)} proxies")
            print(f"{Fore.CYAN}[*] Starting proxy check...")
            
            await self.check_proxies_batch(proxies, protocol)

            self.stats['invalid'] = self.stats['total'] - self.stats['valid']
            
            self._display_final_results()
            self.save_results(protocol)

        except FileNotFoundError as e:
            logging.error(f"File not found: {str(e)}")
            print(f"{Fore.RED}[!] {str(e)}")
        except ValueError as e:
            logging.error(f"Value error: {str(e)}")
            print(f"{Fore.RED}[!] {str(e)}")
        except ProxyCheckError as e:
            logging.error(f"Proxy check error: {str(e)}")
            print(f"{Fore.RED}[!] {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            print(f"{Fore.RED}[!] An unexpected error occurred: {str(e)}")
        finally:
            print(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            input()

    def _get_protocol_choice(self) -> Optional[str]:
        try:
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
                return None

            return protocol

        except Exception as e:
            logging.error(f"Error getting protocol choice: {str(e)}")
            return None

    def _load_proxies(self, filepath: str) -> list:
        try:
            with open(filepath, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            logging.error(f"Error loading proxies from file: {str(e)}")
            raise

    def _display_final_results(self) -> None:
        try:
            print(f"\n{Fore.CYAN}═══ Check Complete ═══")
            print(f"{Fore.GREEN}Valid Proxies: {self.stats['valid']}")
            print(f"{Fore.RED}Invalid Proxies: {self.stats['invalid']}")
            print(f"{Fore.YELLOW}Average Speed: {self.stats['average_speed']:.2f}s")
            print(f"{Fore.RED}Errors: {self.stats['errors']}")
        except Exception as e:
            logging.error(f"Error displaying final results: {str(e)}")

if __name__ == "__main__":
    try:
        checker = RushProxyChecker()
        asyncio.run(checker.start())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Proxy checker stopped by user.")
    except Exception as e:
        logging.critical(f"Critical error in main: {str(e)}")
        print(f"{Fore.RED}Critical error occurred. Check proxy_checker.log for details.")
