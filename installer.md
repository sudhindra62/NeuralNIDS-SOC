# AegisGAN Native Linux Deployment Guide

This guide contains all the commands you need to package the AegisGAN platform from your current machine and deploy it as a persistent, automatically-running background service on any other Linux machine.

## Phase 1: Package the App (On your current Windows machine)

Before you can move the app to a Linux server, you need to compress the entire project directory into a ZIP file. 

Open PowerShell and navigate to the folder containing the project, then run:

```powershell
# Compress the AegisGAN_live folder into a zip file
Compress-Archive -Path e:\AegisGAN_live -DestinationPath e:\AegisGAN_live.zip
```

*(Alternatively, you can just right-click the `AegisGAN_live` folder in File Explorer and select "Compress to ZIP file".)*

## Phase 2: Transfer the App to the Linux Server

You need to send the `AegisGAN_live.zip` file to your Linux machine. You can use a tool like WinSCP, FileZilla, or the `scp` command in PowerShell.

```powershell
# Example SCP command (Replace 'user' and '192.168.1.100' with your Linux details)
scp e:\AegisGAN_live.zip user@192.168.1.100:~
```

## Phase 3: Install the App (On the target Linux machine)

Log into your Linux machine via SSH. The following commands will unzip the project and run the automated installer. 

The installer will automatically install Zeek, Python, Node.js, and configure the background system services.

```bash
# 1. Update package lists (Recommended before installing things)
sudo apt update

# 2. Install 'unzip' in case the Linux server doesn't have it
sudo apt install unzip -y

# 3. Unzip the project folder you transferred
unzip AegisGAN_live.zip

# 4. Navigate into the unzipped project folder
cd AegisGAN_live

# 5. Make the automated installation script executable
chmod +x installer/install.sh

# 6. Run the installer as root
sudo ./installer/install.sh
```

**Note:** The installation might take a few minutes as it downloads dependencies and builds the React frontend.

## Phase 4: Verify and Manage Services

Once the installation script finishes, AegisGAN is officially running in the background! It is managed by `systemctl`, meaning it will automatically start itself even if the server reboots.

Here are the commands you can use to check the status or restart the system:

```bash
# Check the status of the FastAPI ML Backend
sudo systemctl status aegisgan-backend

# Check the status of the React Frontend
sudo systemctl status aegisgan-frontend

# Check the status of the Zeek Log Streaming Bridge
sudo systemctl status aegisgan-bridge
```

If you ever need to restart the entire platform:
```bash
sudo systemctl restart aegisgan-backend aegisgan-frontend aegisgan-bridge
```

If you want to view the live terminal output/logs of the background ML backend:
```bash
sudo journalctl -fu aegisgan-backend
```

## Phase 5: Access the Dashboard

The system is now sniffing network traffic in real-time and running inference!

To view the live SOC Dashboard, open a web browser on any machine on the same network and navigate to the Linux server's IP address on port `5173`:

```text
http://<LINUX_SERVER_IP>:5173
```
*(Example: `http://192.168.1.100:5173`)*



