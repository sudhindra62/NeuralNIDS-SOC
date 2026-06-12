# backend/services/alert_service.py
import asyncio
from storage.memory_store import store
from api.websocket import manager
from shared.utils import get_timestamp
import random

import random

async def process_prediction(label, confidence, flow_details):
    """
    Handles model output. If attack detected, creates an alert and broadcasts.
    """
    alert = {
        "timestamp": get_timestamp(),
        "label": label,
        "confidence": round(confidence, 4),
        "src_ip": flow_details.get('src_ip'),
        "dst_ip": flow_details.get('dst_ip'),
        "src_port": flow_details.get('src_port'),
        "dst_port": flow_details.get('dst_port'),
        "proto": flow_details.get('proto'),
        "service": flow_details.get('service'),
        "sbytes": flow_details.get('sbytes', 0),
        "dbytes": flow_details.get('dbytes', 0),
        "state": flow_details.get('state', '-'),
        "duration": flow_details.get('duration', 0)
    }



    if label != "Normal":
        store.add_alert(alert)
        # Broadcast to WebSocket
        await manager.broadcast({
            "type": "ALERT",
            "data": alert
        })
    else:
        # Just broadcast flow for stats/live view
        await manager.broadcast({
            "type": "FLOW",
            "data": alert
        })
    
    # Update global stats
    # Stats are updated inside MemoryStore implicitly if we want, or here
    if label == "Normal":
        store.traffic_stats["normal"] += 1
    else:
        # attacks already incremented in add_alert?
        # Let's keep it consistent
        pass
