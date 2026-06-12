# bridge/format_parser.py

class ZeekConnParser:
    def __init__(self):
        self.fields = []
        
    def parse_header(self, line):
        """Parses the #fields line from Zeek log"""
        if line.startswith("#fields"):
            self.fields = line.strip().split("\t")[1:]
            return True
        return False

    def parse_line(self, line):
        """Parses a single log line into a dictionary"""
        if not self.fields:
            return None
        
        if line.startswith("#"):
            return None
            
        values = line.strip().split("\t")
        if len(values) != len(self.fields):
            return None
            
        return dict(zip(self.fields, values))

    def clean_dict(self, flow_dict):
        """Standardizes fields for the ML pipeline"""
        if not flow_dict:
            return None
            
        # Rename fields to match ML requirements
        mapping = {
            'proto': 'proto',
            'duration': 'dur',
            'orig_pkts': 'spkts',
            'resp_pkts': 'dpkts',
            'orig_bytes': 'sbytes',
            'resp_bytes': 'dbytes',
            'conn_state': 'state',
            'orig_ip_bytes': 'sload_raw', # Helper for sload
            'resp_ip_bytes': 'dload_raw', # Helper for dload
            'id.orig_h': 'src_ip',
            'id.resp_h': 'dst_ip',
            'id.orig_p': 'src_port',
            'id.resp_p': 'dst_port',
            'service': 'service',
            'orig_ttl': 'sttl', # Note: Zeek may not have sttl/dttl in default conn.log
            'resp_ttl': 'dttl'  # We might need to add these or default them
        }
        
        cleaned = {}
        for zeek_key, ml_key in mapping.items():
            cleaned[ml_key] = flow_dict.get(zeek_key, "-")
            
        # Default missing but required features
        if cleaned.get('sttl') == "-": cleaned['sttl'] = 0
        if cleaned.get('dttl') == "-": cleaned['dttl'] = 0
        
        return cleaned
