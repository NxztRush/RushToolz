import json
import os

class Config:
    def __init__(self):
        self.config_file = 'config/settings.json'
        self.settings = {
            'threads': 100,
            'timeout': 10,
            'retry_attempts': 3,
            'proxy_rotation': True,
            'save_format': 'json',
            'webhook_enabled': True,
            'webhook_url': 'YOUR_WEBHOOK_URL',
            'check_urls': [
                'https://google.com',
                'https://example.com',
                'https://cloudflare.com'
            ],
            'proxy_sources': {
                'http': [
                    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
                    'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http'
                ],
                'https': [
                    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/https.txt',
                    'https://api.proxyscrape.com/v2/?request=getproxies&protocol=https'
                ],
                'socks4': [
                    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
                    'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4'
                ],
                'socks5': [
                    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
                    'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5'
                ]
            }
        }
        self.load()

    def save(self):
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def load(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                loaded_settings = json.load(f)
                self.settings.update(loaded_settings)

    def get(self, key):
        return self.settings.get(key)

    def set(self, key, value):
        self.settings[key] = value
        self.save()
