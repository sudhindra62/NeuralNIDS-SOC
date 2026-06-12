# backend/features/builder.py
import pandas as pd
from .streaming_ct import stateful_counters
from shared.features import MODEL_FEATURES

# Zeek state to UNSW-NB15 state mapping
STATE_MAP = {
    'SF': 'FIN',
    'S0': 'INT',
    'S1': 'FIN',
    'S2': 'FIN',
    'S3': 'FIN',
    'OTH': 'CON',
    'REJ': 'RST',
    'RSTO': 'RST',
    'RSTR': 'RST',
    'SH': 'INT',
    'SHR': 'FIN',
    'RSTOS0': 'RST'
}

class FeatureBuilder:
    def __init__(self):
        pass

    def build(self, raw_flow):
        """Transforms raw Zeek flow into the 15 ML features"""
        
        # 1. Basic conversions
        try:
            dur = float(raw_flow.get('dur', 0))
        except:
            dur = 0.0
            
        z_state = raw_flow.get('state', 'OTH').upper()
        mapped_state = STATE_MAP.get(z_state, 'CON')
            
        try:
            sbytes = int(raw_flow.get('sbytes', 0))
            dbytes = int(raw_flow.get('dbytes', 0))
            spkts = int(raw_flow.get('spkts', 0))
            dpkts = int(raw_flow.get('dpkts', 0))
        except:
            sbytes, dbytes, spkts, dpkts = 0, 0, 0, 0

        # 2. Derived features
        sload = (sbytes * 8) / dur if dur > 0 else 0
        dload = (dbytes * 8) / dur if dur > 0 else 0
        
        # Loss calculation (simplified for real-time if not in Zeek)
        sloss = 0 
        dloss = 0

        # 3. Stateful features
        ct_features = stateful_counters.update_and_calculate(raw_flow)
        
        # 4. Construct final dict
        # 4. Protocol-Aware Feature Imputation
        proto_lower = raw_flow.get('proto', 'tcp').lower()
        
        # Base TTLs based on protocol behavior
        default_sttl = 62
        default_dttl = 252
        
        if proto_lower == 'udp':
            default_sttl, default_dttl = 64, 255
        elif proto_lower == 'tcp':
            default_sttl, default_dttl = 128, 252
        elif proto_lower == 'icmp':
            default_sttl, default_dttl = 64, 0
            
        sttl_raw = int(raw_flow.get('sttl', default_sttl)) if raw_flow.get('sttl', '-') != '-' else default_sttl
        dttl_raw = int(raw_flow.get('dttl', default_dttl)) if raw_flow.get('dttl', '-') != '-' else default_dttl
        
        features = {
            'proto': proto_lower,
            'state': mapped_state,
            'dur': dur,
            'spkts': spkts,
            'dpkts': dpkts,
            'sbytes': sbytes,
            'dbytes': dbytes,
            'sttl': sttl_raw if sttl_raw > 0 else default_sttl,
            'dttl': dttl_raw if dttl_raw > 0 else default_dttl,
            'sload': sload,
            'dload': dload,
            'sloss': sloss,
            'dloss': dloss,
            'ct_srv_src': ct_features['ct_srv_src'],
            'ct_dst_ltm': ct_features['ct_dst_ltm']
        }
        
        return features

    def to_dataframe(self, feature_list):
        """Converts a list of feature dicts to a DataFrame in correct order"""
        df = pd.DataFrame(feature_list)
        return df[MODEL_FEATURES]

builder = FeatureBuilder()
