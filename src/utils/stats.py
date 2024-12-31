import time
from datetime import datetime

class Statistics:
    def __init__(self):
        self.start_time = time.time()
        self.hits = 0
        self.fails = 0
        self.retries = 0
        self.cpm_data = []
        self.response_times = []
        
    def update_cpm(self):
        current_minute = int((time.time() - self.start_time) / 60)
        while len(self.cpm_data) <= current_minute:
            self.cpm_data.append(0)
        self.cpm_data[current_minute] += 1
    
    def get_current_cpm(self):
        return self.cpm_data[-1] if self.cpm_data else 0
    
    def get_peak_cpm(self):
        return max(self.cpm_data) if self.cpm_data else 0
    
    def get_stats_report(self):
        runtime = time.time() - self.start_time
        return {
            'runtime': f"{runtime:.2f}s",
            'hits': self.hits,
            'fails': self.fails,
            'retries': self.retries,
            'success_rate': f"{(self.hits / (self.hits + self.fails) * 100):.2f}%" if (self.hits + self.fails) > 0 else "0%",
            'current_cpm': self.get_current_cpm(),
            'peak_cpm': self.get_peak_cpm(),
            'avg_response': f"{(sum(self.response_times) / len(self.response_times)):.2f}s" if self.response_times else "0s"
        }
