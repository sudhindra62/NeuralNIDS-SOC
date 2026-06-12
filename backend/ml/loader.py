# backend/ml/loader.py
import joblib
from xgboost import XGBClassifier
from shared.config import (
    MODEL_PATH, PREPROCESSOR_PATH, LABEL_ENCODER_PATH, FEATURE_ORDER_PATH
)

def load_ml_artifacts():
    from shared.config import MODEL_PHASE2_PATH, THRESHOLDS_PATH, ARTIFACTS_DIR
    import tensorflow as tf
    from ml.threshold_tuning import ThresholdTuner
    
    print(f"Loading Phase-3 XGBoost model from {MODEL_PHASE2_PATH}...")
    # It's a pickle file containing the fitted XGBoost model, not json
    xgb_model = joblib.load(MODEL_PHASE2_PATH)
    
    # We need the CNN-LSTM model too for the ensemble
    CNN_LSTM_PATH = ARTIFACTS_DIR / "cnn_lstm_improved_model.keras"
    print(f"Loading Phase-3 CNN-LSTM model from {CNN_LSTM_PATH}...")
    cnn_model = tf.keras.models.load_model(str(CNN_LSTM_PATH))
    
    print(f"Loading preprocessor from {PREPROCESSOR_PATH}...")
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    
    print(f"Loading label encoder from {LABEL_ENCODER_PATH}...")
    label_encoder = joblib.load(LABEL_ENCODER_PATH)
    
    print(f"Loading feature order from {FEATURE_ORDER_PATH}...")
    feature_order = joblib.load(FEATURE_ORDER_PATH)
    
    from shared.config import ARTIFACTS_DIR
    proto_encoder = joblib.load(ARTIFACTS_DIR / "proto_encoder.pkl")
    state_encoder = joblib.load(ARTIFACTS_DIR / "state_encoder.pkl")
    
    print(f"Loading Threshold Tuner from {THRESHOLDS_PATH}...")
    tuner = joblib.load(THRESHOLDS_PATH)
        
    return xgb_model, cnn_model, tuner, preprocessor, label_encoder, feature_order, proto_encoder, state_encoder

class MLAssets:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLAssets, cls).__new__(cls)
            cls._instance.xgb_model, cls._instance.cnn_model, cls._instance.tuner, \
            cls._instance.preprocessor, cls._instance.label_encoder, \
            cls._instance.feature_order, cls._instance.proto_encoder, \
            cls._instance.state_encoder = load_ml_artifacts()
        return cls._instance

ml_assets = MLAssets()
