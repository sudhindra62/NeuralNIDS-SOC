#!/bin/bash

# run_zeek.sh
# Start Zeek capture on specified interface and output to current directory

INTERFACE=${1:-eth0}
LOG_DIR=${2:-"./logs"}

mkdir -p $LOG_DIR
cd $LOG_DIR

echo "Starting Zeek on interface $INTERFACE..."
echo "Logs will be generated in $(pwd)"

# -i: interface
# local: load local.zeek
# Disable checksum validation for captured traffic (often needed for WSL)
sudo /opt/zeek/bin/zeek -i $INTERFACE -C local "Site::local_nets += { 192.168.0.0/16 }"
