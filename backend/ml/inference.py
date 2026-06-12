# backend/ml/inference.py
import numpy as np
from .loader import ml_assets

def predict_flow(x_xgb, x_cnn):
    """
    Runs Phase-3 Ensemble Inference.
    """
    # 1. Get Probabilities from XGBoost
    xgb_preds = ml_assets.xgb_model.predict_proba(x_xgb)[0]
    
    # 2. Get Probabilities from CNN-LSTM
    cnn_preds = ml_assets.cnn_model.predict(x_cnn, verbose=0)[0]
    
    # 3. Ensemble Average
    combined_preds = (xgb_preds + cnn_preds) / 2.0
    
    # --- Live Traffic Calibration ---
    # The Phase-3 GAN models are extremely sensitive to UDP/DNS traffic anomalies. 
    # To prevent the dashboard from being overwhelmed by false positive 'Analysis' attacks 
    # on harmless background noise, we apply a dampening factor to all attack classes.
    # This compresses the attack probabilities so only genuine, high-confidence anomalies trigger the Threshold Tuner.
    attack_indices = [i for i in range(len(combined_preds)) if i != 6] # Class 6 is Normal
    for i in attack_indices:
        combined_preds[i] *= 0.05 # Compress attack confidence by 95%
        
    # Normalize probabilities back to 1.0
    combined_preds = combined_preds / np.sum(combined_preds)
    
    # 4. Apply Threshold Tuner
    final_pred_idx = int(np.argmax(combined_preds))
    
    # ml_assets.tuner is a dict of {class_idx: threshold}
    # Sort by threshold ascending to prioritize sensitive minority classes
    sorted_indices = sorted(ml_assets.tuner.keys(), key=lambda x: ml_assets.tuner[x])
    for idx in sorted_indices:
        t = ml_assets.tuner[idx]
        if combined_preds[idx] > t:
            final_pred_idx = int(idx)
            break
            
    confidence = float(combined_preds[final_pred_idx])
    
    # 5. Map index to label
    label = ml_assets.label_encoder.inverse_transform([final_pred_idx])[0]
        
    return label, confidence
