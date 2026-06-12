import asyncio
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from core.pipeline import process_new_flow

async def test():
    sample_flow = '{"ts": 1776799516.277371, "uid": "CNMAO14v9EpQPUpZ82", "id.orig_h": "fe80::215:5dff:fe06:3d44", "id.orig_p": 133, "id.resp_h": "ff02::2", "id.resp_p": 134, "proto": "icmp", "service": "-", "duration": "-", "orig_bytes": "-", "resp_bytes": "-", "conn_state": "OTH", "local_orig": "T", "local_resp": "F", "missed_bytes": 0, "history": "-", "orig_pkts": 1, "orig_ip_bytes": 56, "resp_pkts": 0, "resp_ip_bytes": 0, "tunnel_parents": "-", "ip_proto": 58}'
    
    raw_flow = json.loads(sample_flow)
    try:
        await process_new_flow(raw_flow)
        print("Success")
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
