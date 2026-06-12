import socket
import json
import time

def test_backend():
    host = "127.0.0.1"
    port = 9000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print(f"Connecting to {host}:{port}...")
        sock.connect((host, port))
        print("Connected.")
        
        test_flow = {
            "src_ip": "1.2.3.4",
            "dst_ip": "5.6.7.8",
            "src_port": "1234",
            "dst_port": "80",
            "proto": "tcp",
            "service": "http",
            "sbytes": 100,
            "dbytes": 200,
            "state": "SF",
            "dur": 1.0
        }
        
        payload = json.dumps(test_flow) + "\n"
        print(f"Sending test flow: {payload.strip()}")
        sock.sendall(payload.encode('utf-8'))
        print("Sent.")
        time.sleep(1)
        sock.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_backend()
