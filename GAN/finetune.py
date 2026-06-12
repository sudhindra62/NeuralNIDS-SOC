import os
import shutil
import joblib
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.optimizers import Adam
from xgboost import XGBClassifier

def run_finetune():
    print("Loading datasets...")
    # Load Real Data
    real_df = pd.read_csv('ml_training/dataset/unsw_nb_cleaned.csv')
    
    # Load Synthetic Data
    synth_df = pd.read_csv('GAN/synthetic_data.csv')

    features = ['proto', 'state', 'dur', 'spkts', 'dpkts', 'sbytes', 'dbytes', 'sttl', 'dttl', 'sload', 'dload', 'sloss', 'dloss', 'ct_srv_src', 'ct_dst_ltm']
    
    X_real = real_df[features].copy()
    y_real = real_df['attack_cat'].copy()
    
    # Split Real Data (Test set must be exclusively real data)
    X_train_real, X_test, y_train_real, y_test = train_test_split(
        X_real, y_real, test_size=0.15, random_state=42, stratify=y_real
    )
    
    X_synth = synth_df[features].copy()
    y_synth = synth_df['attack_cat'].copy()
    
    # Create sample weights: Real=1.0, Synth=0.5
    weights_real = np.ones(len(X_train_real), dtype=np.float32)
    weights_synth = np.full(len(X_synth), 0.5, dtype=np.float32)
    
    X_combined = pd.concat([X_train_real, X_synth], ignore_index=True)
    y_combined = pd.concat([y_train_real, y_synth], ignore_index=True)
    sample_weights_combined = np.concatenate([weights_real, weights_synth])
    
    print("Preprocessing...")
    for c in ['proto', 'state']:
        le = LabelEncoder()
        # Fit on real data, transform both
        le.fit(X_train_real[c].astype(str))
        X_combined[c] = X_combined[c].map(lambda s: le.transform([s])[0] if s in le.classes_ else -1)
        X_test.loc[:, c] = X_test[c].map(lambda s: le.transform([s])[0] if s in le.classes_ else -1)
    
    scaler = joblib.load('ml_training/artifacts_improved/scaler.pkl')
    label_encoder = joblib.load('ml_training/artifacts_improved/label_encoder.pkl')
    
    X_combined_scaled = scaler.transform(X_combined)
    X_test_scaled = scaler.transform(X_test)
    
    y_combined_enc = label_encoder.transform(y_combined)
    y_test_enc = label_encoder.transform(y_test)
    
    classes = label_encoder.classes_
    
    os.makedirs('GAN/finetune', exist_ok=True)
    shutil.copy('ml_training/artifacts_improved/xgboost_improved_model.json', 'GAN/finetune/xgboost_original.json')
    shutil.copy('ml_training/artifacts_improved/cnn_lstm_improved_model.keras', 'GAN/finetune/cnn_lstm_original.keras')
    
    print("Fine-tuning XGBoost...")
    # XGBoost safe fine-tuning
    xgb_finetuned = XGBClassifier(
        n_estimators=50, # limited boosting rounds
        learning_rate=0.01, # very low learning rate
        max_depth=6,
        tree_method='hist'
    )
    
    xgb_finetuned.fit(
        pd.DataFrame(X_combined_scaled, columns=features), 
        y_combined_enc, 
        sample_weight=sample_weights_combined, 
        xgb_model='GAN/finetune/xgboost_original.json'
    )
    xgb_finetuned.save_model('GAN/finetune/xgboost_finetuned.model')
    
    print("Fine-tuning CNN-LSTM...")
    # CNN-LSTM safe fine-tuning
    cnn_lstm_finetuned = load_model('GAN/finetune/cnn_lstm_original.keras')
    
    # Freeze lower layers (e.g., Conv1D) to prevent forgetting feature extraction
    for layer in cnn_lstm_finetuned.layers[:3]:
        layer.trainable = False
        
    cnn_lstm_finetuned.compile(optimizer=Adam(learning_rate=1e-5), loss='categorical_crossentropy', metrics=['accuracy'])
    
    y_combined_cat = to_categorical(y_combined_enc, num_classes=len(classes))
    y_test_cat = to_categorical(y_test_enc, num_classes=len(classes))
    
    X_combined_seq = np.expand_dims(X_combined_scaled, axis=1)
    X_test_seq = np.expand_dims(X_test_scaled, axis=1)
    
    cnn_lstm_finetuned.fit(
        X_combined_seq, 
        y_combined_cat, 
        sample_weight=sample_weights_combined,
        epochs=3, 
        batch_size=128, 
        validation_split=0.1
    )
    
    cnn_lstm_finetuned.save('GAN/finetune/cnn_lstm_finetuned.keras')
    cnn_lstm_finetuned.save('GAN/finetune/cnn_lstm_finetuned.h5')
    
    print("Fine-tuning complete.")

if __name__ == '__main__':
    run_finetune()
