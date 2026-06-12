# bridge/log_tail.py
import time
import os

class LogTailer:
    def __init__(self, filepath):
        self.filepath = filepath
        self.file = None

    def follow(self, start_at_end=False):
        """Generator that yields new lines in a file"""
        while not os.path.exists(self.filepath):
            print(f"Waiting for {self.filepath} to be created...")
            time.sleep(1)

        self.file = open(self.filepath, "r")
        
        # 1. Read existing headers regardless of start_at_end
        # This ensures the parser gets the #fields line
        if start_at_end:
            print(f"Reading headers and skipping to live data in {self.filepath}...")
            # Read first few lines to find headers
            for _ in range(20): # Check first 20 lines for headers
                pos = self.file.tell()
                line = self.file.readline()
                if not line: break
                if line.startswith("#"):
                    yield line
                else:
                    # Found data, we can stop reading headers
                    break
            
            # Now skip to end for live data
            self.file.seek(0, os.SEEK_END)
        
        while True:
            pos = self.file.tell()
            line = self.file.readline()
            if not line:
                # Handle file truncation/rotation (Zeek restarts)
                if os.path.exists(self.filepath) and os.path.getsize(self.filepath) < pos:
                    print("Log file rotated/truncated. Resetting stream...")
                    self.file.seek(0, 0)
                time.sleep(0.1) # Wait for new data
                continue
            yield line

    def close(self):
        if self.file:
            self.file.close()
            self.file = None
