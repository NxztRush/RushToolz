import re

class PatternMatcher:
    def __init__(self):
        self.patterns = {
            'email': r'^[\w\.-]+@[\w\.-]+\.\w+$',
            'ip': r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$',
            'port': r'^\d{1,5}$',
            'proxy': r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$',
            'url': r'^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$'
        }
    
    def match(self, pattern_name, text):
        if pattern_name in self.patterns:
            return bool(re.match(self.patterns[pattern_name], text))
        return False
    
    def extract(self, pattern_name, text):
        if pattern_name in self.patterns:
            return re.findall(self.patterns[pattern_name], text)
        return []
    
    def add_pattern(self, name, pattern):
        self.patterns[name] = pattern
