import aiohttp
from datetime import datetime

class DiscordWebhook:
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url
        self.headers = {
            "Content-Type": "application/json"
        }

    async def send_hit(self, embed):
        if not self.webhook_url:
            return
            
        async with aiohttp.ClientSession() as session:
            await session.post(
                self.webhook_url,
                json={"embeds": [embed]},
                headers=self.headers
            )

    async def send_notification(self, title, message, color=0x00ff00):
        embed = {
            "title": title,
            "description": message,
            "color": color,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_hit(embed)
