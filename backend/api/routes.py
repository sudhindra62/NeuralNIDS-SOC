# backend/api/routes.py
from fastapi import APIRouter
from storage.memory_store import store

router = APIRouter()

@router.get("/alerts")
async def get_alerts():
    """Returns the last 100 detected attacks"""
    return store.get_alerts()

@router.get("/stats")
async def get_stats():
    """Returns traffic and detection statistics"""
    return store.get_stats()

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/flows")
async def get_flows():
    """Returns the recent flows in the sliding window"""
    return list(store.window)

@router.post("/clear")
async def clear_data():
    """Clears all historical data from memory"""
    store.clear()
    return {"status": "cleared"}
