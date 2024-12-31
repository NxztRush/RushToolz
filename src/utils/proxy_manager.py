import random
from threading import Lock

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.current_index = 0
        self.lock = Lock()
        
    def load_proxies(self, proxy_file):
        with open(proxy_file, 'r') as f:
            self.proxies = [line.strip() for line in f if line.strip()]
        random.shuffle(self.proxies)
    
    def get_next_proxy(self):
        with self.lock:
            if not self.proxies:
                return None
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            return proxy
    
    def remove_proxy(self, proxy):
        with self.lock:
            if proxy in self.proxies:
                self.proxies.remove(proxy)
