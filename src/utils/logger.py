import os
from datetime import datetime
from colorama import Fore, Style

class Logger:
    def __init__(self):
        self.log_dir = 'logs'
        self.log_levels = {
            'DEBUG': (Fore.CYAN, 0),
            'INFO': (Fore.WHITE, 1),
            'SUCCESS': (Fore.GREEN, 2),
            'WARNING': (Fore.YELLOW, 3),
            'ERROR': (Fore.RED, 4),
            'CRITICAL': (Fore.MAGENTA, 5)
        }
        self.current_level = 1
        self.setup_logging()
    
    def setup_logging(self):
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, f'log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
    
    def log(self, message, level='INFO'):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        color, importance = self.log_levels.get(level, (Fore.WHITE, 1))
        
        if importance >= self.current_level:
            console_message = f"{color}[{timestamp}] [{level}] {message}{Style.RESET_ALL}"
            file_message = f"[{timestamp}] [{level}] {message}"
            
            print(console_message)
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(file_message + '\n')
