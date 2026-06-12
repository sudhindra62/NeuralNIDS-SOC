# shared/utils.py
import json
import logging
from datetime import datetime

def setup_logger(name, log_file, level=logging.INFO):
    """Function setup as many loggers as you want"""
    handler = logging.FileHandler(log_file)        
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def serialize_flow(flow_dict):
    return json.dumps(flow_dict)

def deserialize_flow(flow_str):
    return json.loads(flow_str)
