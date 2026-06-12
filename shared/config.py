# shared/config.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ML Configuration
WINDOW_SIZE = 30  # T=30
ARTIFACTS_DIR = BASE_DIR / "ml_training" / "artifacts_improved"
# Phase 3 Ensemble Configuration
GAN_DIR = BASE_DIR / "GAN"
MODEL_ORIG_PATH = GAN_DIR / "finetune" / "xgboost_original.json"
MODEL_PHASE2_PATH = GAN_DIR / "finetune_v2" / "xgboost_finetuned_v2.pkl"
THRESHOLDS_PATH = GAN_DIR / "finetune_v2" / "optimal_thresholds.pkl"

MODEL_PATH = ARTIFACTS_DIR / "xgboost_improved_model.json"
PREPROCESSOR_PATH = ARTIFACTS_DIR / "scaler.pkl"
LABEL_ENCODER_PATH = ARTIFACTS_DIR / "label_encoder.pkl"
FEATURE_ORDER_PATH = BASE_DIR / "ml_training" / "artifacts" / "feature_order.pkl"

# Streaming Configuration
BRIDGE_HOST = "0.0.0.0"
BRIDGE_PORT = 9000  # WSL -> Windows streaming port
WS_PORT = 8000      # FastAPI port

# Zeek Configuration
ZEEK_LOG_PATH = "/usr/local/zeek/logs/current/conn.log" # Default path in many Zeek installations
ZEEK_INTERFACE = "eth0"

# Feature State Configuration
STATE_WINDOW_SIZE = 100 # For ct_* features
