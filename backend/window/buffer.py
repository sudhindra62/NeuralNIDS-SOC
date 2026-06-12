# backend/window/buffer.py
from collections import deque
import numpy as np
from shared.config import WINDOW_SIZE

class SlidingWindowBuffer:
    def __init__(self, size=WINDOW_SIZE):
        self.size = size
        self.buffer = deque(maxlen=size)

    def add(self, feature_vector):
        """Adds a new feature vector to the buffer"""
        self.buffer.append(feature_vector)

    def is_ready(self):
        """Returns True if the buffer has at least 1 flow"""
        return len(self.buffer) > 0

    def get_window(self):
        """Returns the current window as a list of dicts"""
        return list(self.buffer)

    def get_window_array(self, preprocessor):
        """
        Returns the latest flow as a preprocessed numpy array (1, input_dim) for XGBoost.
        """
        import pandas as pd
        from shared.features import MODEL_FEATURES
        
        # 1. To DataFrame
        df = pd.DataFrame(list(self.buffer))
        df = df[MODEL_FEATURES]
        
        # 1.5 Apply Label Encoding for categorical features as expected by new pipeline
        from ml.loader import ml_assets
        
        if 'proto' in df.columns:
            df['proto'] = df['proto'].map(lambda s: ml_assets.proto_encoder.transform([s])[0] if s in ml_assets.proto_encoder.classes_ else -1)
            
        if 'state' in df.columns:
            df['state'] = df['state'].map(lambda s: ml_assets.state_encoder.transform([s])[0] if s in ml_assets.state_encoder.classes_ else -1)
                
        # 2. Preprocess
        X = preprocessor.transform(df).astype(np.float32) # (N, input_dim)
        
        # 3. XGBoost format (latest flow only): (1, input_dim)
        x_xgb = X[-1:] 
        
        # 4. CNN-LSTM format (sequence of flows): (1, WINDOW_SIZE, input_dim)
        seq = np.zeros((self.size, X.shape[1]), dtype=np.float32)
        seq[-len(X):] = X
        x_cnn = np.expand_dims(seq, axis=0)
        
        return x_xgb, x_cnn
# Global buffer
window_buffer = SlidingWindowBuffer()
