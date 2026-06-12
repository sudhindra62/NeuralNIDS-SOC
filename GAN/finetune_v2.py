import os
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from xgboost import XGBClassifier
from tensorflow.keras.models import load_model
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from calibration import calibrate_model

def run_finetune_v2():
    print("Starting Phase 2 Fine-Tuning...")
    
    # Create directory if not exists
    os.makedirs('GAN/finetune_v2', exist_ok=True)
    
    # 1. Load Real Data
    print("Loading real dataset...")
    real_df = pd.read_csv('ml_training/dataset/unsw_nb_cleaned.csv')
    features = ['proto', 'state', 'dur', 'spkts', 'dpkts', 'sbytes', 'dbytes', 'sttl', 'dttl', 'sload', 'dload', 'sloss', 'dloss', 'ct_srv_src', 'ct_dst_ltm']
    X_real = real_df[features].copy()
    y_real = real_df['attack_cat'].copy()
    
    # 2. Load Refined Synthetic Data (Filtered)
    print("Loading refined synthetic data...")
    if not os.path.exists('GAN/refined_synthetic_data.csv'):
        print("Error: refined_synthetic_data.csv not found. Run filter.py first.")
        return
    synth_df = pd.read_csv('GAN/refined_synthetic_data.csv')
    
    # MANDATORY: Use GAN data ONLY for: Analysis, Backdoor, Shellcode, Worms
    target_minority = ['Analysis', 'Backdoor', 'Shellcode', 'Worms']
    synth_df = synth_df[synth_df['attack_cat'].isin(target_minority)]
    
    # 3. Limit Synthetic Data to 15-20% of total
    total_real = len(real_df)
    # Max synth = 0.2 * (total_real + max_synth) => max_synth = 0.25 * total_real
    max_synth = int(0.2 * total_real) 
    if len(synth_df) > max_synth:
        print(f"Downsampling synthetic data from {len(synth_df)} to {max_synth} to maintain <20% ratio.")
        synth_df = synth_df.sample(max_synth, random_state=42)
    
    print(f"Final training set composition: {total_real} Real samples, {len(synth_df)} Synthetic samples.")
    
    # 4. Preprocessing
    print("Preprocessing data...")
    # Load encoders from artifacts_improved (Phase 1 verified these were correct)
    scaler = joblib.load('ml_training/artifacts_improved/scaler.pkl')
    label_encoder = joblib.load('ml_training/artifacts_improved/label_encoder.pkl')
    
    # Manual Label Encoding for proto/state as per pipeline
    for c in ['proto', 'state']:
        le = LabelEncoder()
        le.fit(real_df[c].astype(str))
        X_real[c] = le.transform(X_real[c].astype(str))
        synth_df[c] = synth_df[c].map(lambda s: le.transform([s])[0] if s in le.classes_ else -1)
    
    X_real_scaled = scaler.transform(X_real)
    X_synth_scaled = scaler.transform(synth_df[features])
    
    y_real_enc = label_encoder.transform(y_real)
    y_synth_enc = label_encoder.transform(synth_df['attack_cat'])
    
    # 5. Prepare Combined Data for XGBoost
    X_combined = np.vstack([X_real_scaled, X_synth_scaled])
    y_combined = np.concatenate([y_real_enc, y_synth_enc])
    
    # MANDATORY Sample Weighting: Real=1.0, Synth=0.3
    weights_real = np.ones(len(y_real_enc))
    # Penalty for dominant classes: Generic, Normal, DoS
    dominant_indices = [label_encoder.transform([c])[0] for c in ['Generic', 'Normal', 'DoS']]
    for i, label in enumerate(y_real_enc):
        if label in dominant_indices:
            weights_real[i] = 0.9 # Slight penalty to reduce bias
            
    weights_synth = np.full(len(y_synth_enc), 0.3)
    sample_weights_combined = np.concatenate([weights_real, weights_synth])
    
    # 6. Fine-Tune XGBoost v2
    print("Fine-tuning XGBoost v2...")
    xgb_v2 = XGBClassifier(
        n_estimators=50,
        learning_rate=0.01,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        use_label_encoder=False,
        eval_metric='mlogloss'
    )
    
    # Split for calibration validation
    X_train, X_val, y_train, y_val, w_train, w_val = train_test_split(
        X_combined, y_combined, sample_weights_combined, test_size=0.1, random_state=42, stratify=y_combined
    )
    
    xgb_v2.fit(
        pd.DataFrame(X_train, columns=features), 
        y_train, 
        sample_weight=w_train, 
        xgb_model='GAN/finetune/xgboost_original.json'
    )
    
    # Apply Probability Calibration
    calibrated_xgb = calibrate_model(xgb_v2, X_val, y_val)
    
    # Save XGBoost v2
    joblib.dump(calibrated_xgb, 'GAN/finetune_v2/xgboost_finetuned_v2.pkl')
    # Note: calibrated model is saved as pkl because it's a sklearn wrapper
    print("XGBoost v2 saved to GAN/finetune_v2/xgboost_finetuned_v2.pkl")
    
    # 7. Fine-Tune CNN-LSTM v2
    print("\nFine-tuning CNN-LSTM v2...")
    # Training data: 90% real + 10% filtered synthetic (MANDATORY)
    num_synth_for_cnn = int(0.1 * len(real_df))
    synth_for_cnn = synth_df.sample(min(len(synth_df), num_synth_for_cnn), random_state=42)
    X_synth_cnn = scaler.transform(synth_for_cnn[features])
    y_synth_cnn = label_encoder.transform(synth_for_cnn['attack_cat'])
    
    X_combined_cnn = np.vstack([X_real_scaled, X_synth_cnn])
    y_combined_cnn = np.concatenate([y_real_enc, y_synth_cnn])
    
    # Reshape for CNN-LSTM (N, 1, 15)
    X_combined_cnn_seq = np.expand_dims(X_combined_cnn, axis=1)
    
    cnn_v2 = load_model('GAN/finetune/cnn_lstm_original.keras')
    
    # Freeze early layers (CNN backbone) - Assuming layers 0-2 are CNN
    for layer in cnn_v2.layers[:3]:
        layer.trainable = False
        
    cnn_v2.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5), 
                   loss='sparse_categorical_crossentropy', 
                   metrics=['accuracy'])
    
    cnn_v2.fit(
        X_combined_cnn_seq, y_combined_cnn,
        epochs=5,
        batch_size=64,
        validation_split=0.1,
        verbose=1
    )
    
    cnn_v2.save('GAN/finetune_v2/cnn_lstm_finetuned_v2.keras')
    print("CNN-LSTM v2 saved to GAN/finetune_v2/cnn_lstm_finetuned_v2.keras")

if __name__ == '__main__':
    import tensorflow as tf
    run_finetune_v2()
