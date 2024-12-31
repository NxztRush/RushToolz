import asyncio
import time
from collections import deque

class RateLimiter:
    def __init__(self, requests_per_second):
        self.rate = requests_per_second
        self.last_check = time.time()
        self.tokens = requests_per_second
        self.requests = deque()
        
    async def acquire(self):
        current = time.time()
        time_passed = current - self.last_check
        self.last_check = current
        
        self.tokens = min(self.rate, self.tokens + time_passed * self.rate)
        
        if self.tokens < 1:
            wait_time = (1 - self.tokens) / self.rate
            await asyncio.sleep(wait_time)
            self.tokens = 0
        else:
            self.tokens -= 1
