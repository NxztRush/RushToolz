class ResultFilter:
    def __init__(self):
        self.filters = {
            'speed': lambda x, v: float(x['speed'].replace('s', '')) <= float(v),
            'reliability': lambda x, v: int(x['reliability'].replace('%', '')) >= int(v),
            'protocol': lambda x, v: x['protocol'].lower() == v.lower()
        }
    
    def apply_filters(self, data, criteria):
        filtered_data = data
        for key, value in criteria.items():
            if key in self.filters:
                filtered_data = [x for x in filtered_data if self.filters[key](x, value)]
        return filtered_data
