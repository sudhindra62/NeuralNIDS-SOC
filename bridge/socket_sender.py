# bridge/socket_sender.py
import socket
import json
import argparse
from log_tail import LogTailer
from format_parser import ZeekConnParser

def stream_logs(log_path, host, port):
    parser = ZeekConnParser()
    import time
    
    while True:
        tailer = LogTailer(log_path)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Connect to Backend
        connected = False
        while not connected:
            try:
                print(f"Connecting to Windows backend at {host}:{port}...")
                sock.connect((host, port))
                print("Connected successfully.")
                connected = True
            except Exception as e:
                print("Backend not ready or disconnected. Retrying in 5 seconds...")
                time.sleep(5)
                
        # Stream live logs
        try:
            # start_at_end=True ensures we only read NEW logs (live traffic)
            for line in tailer.follow(start_at_end=True):
                if parser.parse_header(line):
                    print(f"Parsed headers: {parser.fields}")
                    continue
                
                raw_dict = parser.parse_line(line)
                if raw_dict:
                    cleaned = parser.clean_dict(raw_dict)
                    if cleaned:
                        payload = json.dumps(cleaned) + "\n"
                        sock.sendall(payload.encode('utf-8'))
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            print("Backend connection lost. Initiating reconnect sequence...")
        except KeyboardInterrupt:
            print("Stopping stream...")
            sock.close()
            tailer.close()
            return
        except Exception as e:
            print(f"Stream error: {e}")
            
        # Cleanup before reconnect
        sock.close()
        tailer.close()
        time.sleep(2)

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Stream Zeek logs to Windows Backend")
    arg_parser.add_argument("--path", default="./logs/conn.log", help="Path to conn.log")
    arg_parser.add_argument("--host", default="127.0.0.1", help="Backend Windows IP")
    arg_parser.add_argument("--port", type=int, default=9000, help="Backend Socket Port")
    
    args = arg_parser.parse_args()
    stream_logs(args.path, args.host, args.port)
