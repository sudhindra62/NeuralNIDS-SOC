import asyncio
import websockets
import json
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import uvicorn
from database import engine, SessionLocal, Base, AttackLog, init_db

app = FastAPI(title="AegisGAN Database Microservice")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def listen_to_main_backend():
    uri = "ws://127.0.0.1:8000/ws"
    print(f"[*] Attempting to connect to main backend at {uri}")
    
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print("[*] Successfully connected to main backend stream.")
                while True:
                    message = await websocket.recv()
                    try:
                        data = json.loads(message)
                        if data.get("type") == "ALERT":
                            alert = data.get("data", {})
                            
                            # Do not save normal traffic as attacks
                            label = str(alert.get("label", alert.get("prediction", "")))
                            if label.lower() == "normal":
                                continue

                            db = SessionLocal()
                            try:
                                new_log = AttackLog(
                                    timestamp=str(alert.get("timestamp", "")),
                                    src_ip=str(alert.get("src_ip", "")),
                                    dst_ip=str(alert.get("dst_ip", "")),
                                    dst_port=str(alert.get("dst_port", alert.get("dport", ""))),
                                    proto=str(alert.get("proto", "")),
                                    service=str(alert.get("service", "")),
                                    label=label,
                                    confidence=float(alert.get("confidence", 0.0)),
                                    duration=float(alert.get("duration", 0.0)),
                                    sbytes=int(alert.get("sbytes", 0)),
                                    dbytes=int(alert.get("dbytes", 0)),
                                    state=str(alert.get("state", ""))
                                )
                                db.add(new_log)
                                db.commit()
                                print(f"[DB] Logged Attack from {new_log.src_ip} -> {new_log.label}")
                            except Exception as e:
                                print(f"[DB Error] Could not save log: {e}")
                                db.rollback()
                            finally:
                                db.close()
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"[WS Warning] Connection to main backend lost/failed: {e}. Retrying in 5s...")
            await asyncio.sleep(5)

@app.on_event("startup")
async def startup_event():
    print("[*] Initializing Database...")
    init_db()
    print("[*] Starting WebSocket client task...")
    asyncio.create_task(listen_to_main_backend())

@app.get("/api/logs")
def get_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logs = db.query(AttackLog).order_by(AttackLog.id.desc()).offset(skip).limit(limit).all()
    return logs

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
