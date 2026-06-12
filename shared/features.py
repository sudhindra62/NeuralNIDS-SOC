# shared/features.py

# Strict feature order as expected by the CNN-LSTM model
MODEL_FEATURES = [
    'proto',
    'state',
    'dur',
    'spkts',
    'dpkts',
    'sbytes',
    'dbytes',
    'sttl',
    'dttl',
    'sload',
    'dload',
    'sloss',
    'dloss',
    'ct_srv_src',
    'ct_dst_ltm'
]

# Mapping from Zeek conn.log fields to our internal format
# Zeek field indices (approximate, usually TSV)
# conn.log fields: ts, uid, id.orig_h, id.orig_p, id.resp_h, id.resp_p, proto, service, duration, orig_bytes, resp_bytes, conn_state, local_orig, local_resp, missed_bytes, history, orig_pkts, orig_ip_bytes, resp_pkts, resp_ip_bytes, tunnel_parents
ZEEK_MAPPING = {
    'proto': 'proto',
    'duration': 'dur',
    'orig_pkts': 'spkts',
    'resp_pkts': 'dpkts',
    'orig_bytes': 'sbytes',
    'resp_bytes': 'dbytes',
    'conn_state': 'state',
    # To be calculated: sttl, dttl, sload, dload, sloss, dloss, ct_srv_src, ct_dst_ltm
}
