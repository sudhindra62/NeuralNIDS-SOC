import websocket
import threading
import time

def on_message(ws, message):
    print(f"Received: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"### closed with status {close_status_code}: {close_msg} ###")

def on_open(ws):
    print("Opened connection")

if __name__ == "__main__":
    websocket.enableTrace(True)
    # The correct way to send custom headers in run_forever is through the constructor 
    # and then suppress the default origin.
    ws = websocket.WebSocketApp("ws://127.0.0.1:8000/ws",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close,
                              header=["Origin: http://localhost:5173"])
    
    # We suppress the default origin to avoid the "multiple values" error
    ws.run_forever(suppress_origin=True)
