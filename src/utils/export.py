import json
import csv
import os
from datetime import datetime

class Exporter:
    def __init__(self):
        self.export_dir = 'results/exports'
        os.makedirs(self.export_dir, exist_ok=True)
        
    def export_json(self, data, filename):
        filepath = os.path.join(self.export_dir, f"{filename}_{self.get_timestamp()}.json")
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        return filepath
    
    def export_csv(self, data, filename):
        filepath = os.path.join(self.export_dir, f"{filename}_{self.get_timestamp()}.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        return filepath
    
    def export_txt(self, data, filename):
        filepath = os.path.join(self.export_dir, f"{filename}_{self.get_timestamp()}.txt")
        with open(filepath, 'w') as f:
            for item in data:
                f.write(f"{str(item)}\n")
        return filepath
    
    def get_timestamp(self):
        return datetime.now().strftime("%Y%m%d_%H%M%S")
