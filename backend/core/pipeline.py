# backend/core/pipeline.py
import asyncio
from features.builder import builder
from window.buffer import window_buffer
from ml.inference import predict_flow
from ml.loader import ml_assets
from services.alert_service import process_prediction
from storage.memory_store import store

def apply_heuristics(flow_meta):
    """
    Industry-standard heuristic pre-filtering.
    If traffic matches known benign patterns, return 'Normal' and confidence.
    Else return None.
    """
    proto = str(flow_meta.get('proto', '')).lower()
    port = str(flow_meta.get('dst_port', ''))
    sbytes = flow_meta.get('sbytes', 0)
    dbytes = flow_meta.get('dbytes', 0)
    
    # 1. DNS Queries (UDP 53, small payload)
    if proto == 'udp' and port == '53' and sbytes < 1000:
        return 'Normal', 0.99
        
    # 2. NTP Sync (UDP 123)
    if proto == 'udp' and port == '123' and sbytes < 500:
        return 'Normal', 0.99
        
    # 3. Local ICMP (small pings)
    if proto == 'icmp' and sbytes < 200 and dbytes < 200:
        return 'Normal', 0.99
        
    # 4. Standard background TCP noise (e.g. small HTTPS polling)
    if proto == 'tcp' and port == '443' and sbytes < 5000 and dbytes < 5000:
        return 'Normal', 0.95
        
    return None, None

async def process_new_flow(raw_flow):
    """
    Main pipeline for every flow received from the bridge.
    1. Feature Engineering
    2. Windowing
    3. Heuristic Filtering
    4. ML Inference
    5. Alerting
    """
    # 1. Feature Engineering (Stateful)
    ml_features = builder.build(raw_flow)
    
    # 2. Add to Sliding Window Buffer
    window_buffer.add(ml_features)
    
    # Track metadata for the UI (src/dst ip etc)
    flow_meta = {
        'src_ip': raw_flow.get('src_ip'),
        'dst_ip': raw_flow.get('dst_ip'),
        'src_port': raw_flow.get('src_port'),
        'dst_port': raw_flow.get('dst_port'),
        'proto': ml_features.get('proto'),
        'service': raw_flow.get('service'),
        'sbytes': ml_features.get('sbytes', 0),
        'dbytes': ml_features.get('dbytes', 0),
        'state': raw_flow.get('conn_state', '-'),
        'duration': ml_features.get('dur', 0)
    }
    
    # 3. If window full (T=30), run inference
    if window_buffer.is_ready():
        # --- ML INFERENCE (Heuristics Disabled to show raw model power) ---
        x_xgb, x_cnn = window_buffer.get_window_array(ml_assets.preprocessor)
        label, confidence = predict_flow(x_xgb, x_cnn)
        
        # 4. Handle prediction (Alerting/Broadcasting)
        await process_prediction(label, confidence, flow_meta)
        
        # Add to memory store with label
        flow_meta['label'] = label
        flow_meta['confidence'] = float(confidence)
        from shared.utils import get_timestamp
        flow_meta['timestamp'] = get_timestamp()
        store.add_flow(flow_meta)
    else:
        # Buffer not full yet, just notify UI of a new flow optionally
        # Or store it as Normal pending
        flow_meta['label'] = 'Normal'
        flow_meta['confidence'] = 1.0
        from shared.utils import get_timestamp
        flow_meta['timestamp'] = get_timestamp()
        store.add_flow(flow_meta)
