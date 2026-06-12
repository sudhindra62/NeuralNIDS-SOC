# backend/storage/memory_store.py
from collections import deque

class MemoryStore:
    def __init__(self, max_alerts=100, window_size=50):
        self.alerts = deque(maxlen=max_alerts)
        self.window = deque(maxlen=window_size)
        self.traffic_stats = {
            "total_flows": 0,
            "attacks": 0,
            "normal": 0
        }
    
    def add_alert(self, alert):
        self.alerts.append(alert)
        self.traffic_stats["attacks"] += 1
        
    def add_flow(self, flow):
        self.window.append(flow)
        self.traffic_stats["total_flows"] += 1
        
    def get_alerts(self):
        return list(self.alerts)
        
    def get_stats(self):
        return self.traffic_stats

    def clear(self):
        self.alerts.clear()
        self.window.clear()
        self.traffic_stats = {
            "total_flows": 0,
            "attacks": 0,
            "normal": 0
        }

# Singleton instance
store = MemoryStore()
