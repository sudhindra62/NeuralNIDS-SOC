import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from api.websocket import manager
from services.stream_service import start_stream_server


app = FastAPI(title="AegisGAN NIDS SOC Backend")

# CORS (React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


# =========================
# WebSocket Endpoint
# =========================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            # Keep connection alive by waiting for client messages
            await websocket.receive_text()

    except WebSocketDisconnect:
        await manager.disconnect(websocket)

    except Exception as e:
        print(f"[WS ERROR] {e}")
        await manager.disconnect(websocket)

    finally:
        await manager.disconnect(websocket)


# =========================
# Startup Event
# =========================
@app.on_event("startup")
async def startup_event():
    # Start Zeek/log streaming bridge
    asyncio.create_task(start_stream_server())
    print("Backend initialization complete.")


# =========================
# Entry Point
# =========================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)