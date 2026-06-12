import websocket
import threading
import time

def on_message(ws, message):
    print(f"Received: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")

if __name__ == "__main__":
    websocket.enableTrace(True)
    # Testing with ONLY the browser's origin, no defaults
    ws = websocket.WebSocketApp("ws://127.0.0.1:8000/ws",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    
    # We set the origin manually in the run_forever call or similar if needed, 
    # but let's try to just use the default and see if it works with localhost first.
    ws.run_forever(suppress_origin=True, header=["Origin: http://localhost:5173"])
