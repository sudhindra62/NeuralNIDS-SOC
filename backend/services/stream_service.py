# backend/services/stream_service.py
import asyncio
import json
from core.pipeline import process_new_flow
from shared.config import BRIDGE_HOST, BRIDGE_PORT

async def handle_client(reader, writer):
    """
    Handles connection from the WSL bridge.
    Reads lines of JSON and feeds them into the pipeline.
    """
    addr = writer.get_extra_info('peername')
    print(f"Connection established from bridge at {addr}")
    
    try:
        while True:
            data = await reader.readline()
            if not data:
                break
                
            line = data.decode('utf-8').strip()
            if not line:
                continue
                
            try:
                raw_flow = json.loads(line)
                # Run pipeline asynchronously for each flow
                asyncio.create_task(process_new_flow(raw_flow))
            except json.JSONDecodeError:
                print(f"Malformed JSON received: {line[:50]}...")
            except Exception as e:
                print(f"Error processing flow: {e}")
                
    except Exception as e:
        print(f"Bridge connection error: {e}")
    finally:
        print(f"Closing connection from {addr}")
        writer.close()
        await writer.wait_closed()

async def start_stream_server():
    server = await asyncio.start_server(
        handle_client, '0.0.0.0', BRIDGE_PORT
    )
    
    addr = server.sockets[0].getsockname()
    print(f'Streaming bridge server listening on {addr}')
    
    async with server:
        await server.serve_forever()
