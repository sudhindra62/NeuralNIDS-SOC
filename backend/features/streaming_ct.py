# backend/features/streaming_ct.py
from collections import deque

class StatefulCounters:
    def __init__(self, history_size=100):
        self.history = deque(maxlen=history_size)

    def update_and_calculate(self, flow):
        """
        Updates history with new flow and calculates ct features.
        Required features: ct_srv_src, ct_dst_ltm
        """
        src_ip = flow.get('src_ip')
        dst_ip = flow.get('dst_ip')
        service = flow.get('service', '-')
        
        # Calculate features BEFORE adding to history (or including current)
        # UNSW-NB15 definition: "in 100 connections back of the current connection"
        # Usually implies including the current one.
        
        ct_srv_src = 0
        ct_dst_ltm = 0
        
        for h in self.history:
            if h.get('src_ip') == src_ip and h.get('service') == service:
                ct_srv_src += 1
            if h.get('dst_ip') == dst_ip:
                ct_dst_ltm += 1
        
        # Add current flow to history
        self.history.append({
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'service': service
        })
        
        # Include current connection in counts (it's now in history)
        ct_srv_src += 1
        ct_dst_ltm += 1
        
        return {
            'ct_srv_src': ct_srv_src,
            'ct_dst_ltm': ct_dst_ltm
        }

# Global state
stateful_counters = StatefulCounters()
