# AegisGAN_live: Real-Time NIDS-SOC Streaming System

A production-style Network Intrusion Detection System (NIDS) that integrates Zeek for real-time network traffic capture, a Generative Adversarial Network (GAN) for synthetic data generation and dataset augmentation, and a CNN-LSTM-based deep learning model for intrusion detection. The system is powered by a FastAPI backend for real-time inference and streaming, and a React-based SOC dashboard that provides live visualization of network activity and security alerts.

## Architecture
`Zeek (WSL) -> Bridge (Socket) -> Backend (ML Pipeline) -> React Dashboard (WebSocket)`

## Setup Instructions

### 1. Backend Setup (Windows)
```bash
# Install dependencies
pip install -r requirements.txt

# Start the Backend
python backend/main.py
```

### 2. Frontend Setup (Windows)
```bash
cd frontend
npm install
npm run dev
```

### 3. Zeek Bridge Setup (WSL)
```bash
# 1. Install Zeek in WSL (if not installed)
# 2. Run Zeek capture
wsl
cd /mnt/e/AegisGAN_live/zeek_ws
chmod +x zeek_ws/run_zeek.sh
./zeek_ws/run_zeek.sh eth0

# 3. Start Streaming Bridge (in another terminal)
python bridge/socket_sender.py --path zeek_ws/logs/conn.log --host 127.0.0.1 --port 9000
```

## Features
- **Real-time Streaming**: No batch processing, flows are analyzed as they arrive.
- **CNN-LSTM Model**: High-accuracy intrusion detection trained on UNSW-NB15.
- **Stateful tracking**: Maintains `ct_srv_src` and `ct_dst_ltm` logs for last 100 connections.
- **Live SOC Dashboard**: Vibrant dark-mode UI with real-time alert broadcasting.

## ML Pipeline
- **Window Size (T)**: 30 flows
- **Features**: 15 (strict parity with training)
- **Model**: `final_model96.keras`


.\start_all.bat
