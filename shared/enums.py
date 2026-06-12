# shared/enums.py
from enum import Enum

class AttackType(str, Enum):
    ANALYSIS = "Analysis"
    BACKDOOR = "Backdoor"
    DOS = "DoS"
    EXPLOITS = "Exploits"
    FUZZERS = "Fuzzers"
    GENERIC = "Generic"
    NORMAL = "Normal"
    RECONNAISSANCE = "Reconnaissance"
    SHELLCODE = "Shellcode"
    WORMS = "Worms"

# Reverse mapping if needed
LABEL_TO_ID = {
    "Analysis": 0,
    "Backdoor": 1,
    "DoS": 2,
    "Exploits": 3,
    "Fuzzers": 4,
    "Generic": 5,
    "Normal": 6,
    "Reconnaissance": 7,
    "Shellcode": 8,
    "Worms": 9
}

ID_TO_LABEL = {v: k for k, v in LABEL_TO_ID.items()}
