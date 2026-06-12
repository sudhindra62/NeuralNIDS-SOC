import os
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
from scipy.stats import pearsonr

LATENT_DIM = 64
NUM_CLASSES = 10

def evaluate_correlations(real_data, synth_data):
    # Flatten the correlation matrices and compare their similarity
    real_corr = pd.DataFrame(real_data).corr().fillna(0).values.flatten()
    synth_corr = pd.DataFrame(synth_data).corr().fillna(0).values.flatten()
    
    # Calculate pearson correlation between the two correlation matrices
    corr, _ = pearsonr(real_corr, synth_corr)
    return corr

def generate_data():
    print("Loading real dataset for analysis...")
    df = pd.read_csv('ml_training/dataset/unsw_nb_cleaned.csv')
    
    features = ['proto', 'state', 'dur', 'spkts', 'dpkts', 'sbytes', 'dbytes', 'sttl', 'dttl', 'sload', 'dload', 'sloss', 'dloss', 'ct_srv_src', 'ct_dst_ltm']
    X_real = df[features].copy()
    y_real = df['attack_cat'].copy()
    
    le_dict = {}
    for c in ['proto', 'state']:
        le = LabelEncoder()
        X_real[c] = le.fit_transform(X_real[c].astype(str))
        le_dict[c] = le
        
    scaler = joblib.load('ml_training/artifacts_improved/scaler.pkl')
    X_real_scaled = scaler.transform(X_real).astype(np.float32)
    
    label_encoder = joblib.load('ml_training/artifacts_improved/label_encoder.pkl')
    y_real_encoded = label_encoder.transform(y_real)
    
    print("Identifying minority classes...")
    class_counts = pd.Series(y_real_encoded).value_counts()
    median_count = class_counts.median()
    total_real_samples = len(y_real_encoded)
    
    # Minority classes are those below median count
    minority_classes = class_counts[class_counts < median_count].index.tolist()
    print(f"Minority classes identified: {[label_encoder.classes_[i] for i in minority_classes]}")
    
    generator = tf.keras.models.load_model('GAN/generator.h5', compile=False)
    
    # We want synthetic data to be ~30% of the final dataset
    # target_synth = 0.3 * (total_real + target_synth) => target_synth = 0.3/0.7 * total_real ~ 42% of real
    target_synth_samples = int(0.3 * total_real_samples)
    samples_per_minority_class = target_synth_samples // len(minority_classes)
    
    print(f"Targeting {samples_per_minority_class} samples per minority class.")
    
    synthetic_X_scaled = []
    synthetic_y = []
    
    for cls_idx in minority_classes:
        print(f"\\nGenerating and filtering data for class: {label_encoder.classes_[cls_idx]}")
        # Get real samples for this class to fit IsolationForest
        real_class_data = X_real_scaled[y_real_encoded == cls_idx]
        
        # Fit IsolationForest to catch outliers
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        iso_forest.fit(real_class_data)
        
        valid_samples = []
        batch_size = 5000
        max_retries = 50
        retries = 0
        
        # Generate until we have enough valid samples
        while len(valid_samples) < samples_per_minority_class and retries < max_retries:
            retries += 1
            noise = tf.random.normal((batch_size, LATENT_DIM))
            labels = tf.keras.utils.to_categorical(np.full(batch_size, cls_idx), num_classes=NUM_CLASSES)
            generated = generator.predict([noise, labels], verbose=0)
            
            # Predict outlier (-1) or inlier (1)
            preds = iso_forest.predict(generated)
            inliers = generated[preds == 1]
            
            # Additional check: Does the batch preserve feature correlations?
            # We compare the inliers' correlation matrix to the real data's correlation matrix
            if len(inliers) > 10:
                corr_score = evaluate_correlations(real_class_data, inliers)
                if corr_score > 0.4:  # Relaxed acceptable correlation structure
                    valid_samples.extend(inliers)
                    print(f"  [Batch Accepted] Correlation: {corr_score:.2f}. Total valid: {len(valid_samples)}/{samples_per_minority_class}")
                else:
                    print(f"  [Batch Rejected] Correlation too low: {corr_score:.2f}")
            else:
                print("  [Batch Rejected] Too few inliers passed IsolationForest")
                
        if len(valid_samples) < samples_per_minority_class:
            print(f"  Warning: Reached max retries. Taking {len(valid_samples)} samples instead of {samples_per_minority_class}.")
            
        valid_samples = np.array(valid_samples)[:samples_per_minority_class]
        if len(valid_samples) > 0:
            synthetic_X_scaled.append(valid_samples)
            synthetic_y.append(np.full(len(valid_samples), cls_idx))
            print(f"Successfully generated {len(valid_samples)} filtered samples.")
        else:
            print(f"Failed to generate valid samples for {label_encoder.classes_[cls_idx]}")
        
    synthetic_X_scaled = np.vstack(synthetic_X_scaled)
    synthetic_y = np.concatenate(synthetic_y)
    
    # Inversely transform to raw feature space to match original unsw_nb_cleaned.csv
    synthetic_raw = scaler.inverse_transform(synthetic_X_scaled)
    df_synthetic = pd.DataFrame(synthetic_raw, columns=features)
    
    for c in ['proto', 'state']:
        df_synthetic[c] = np.round(df_synthetic[c]).astype(int)
        df_synthetic[c] = np.clip(df_synthetic[c], 0, len(le_dict[c].classes_) - 1)
        df_synthetic[c] = le_dict[c].inverse_transform(df_synthetic[c])
        
    df_synthetic['attack_cat'] = label_encoder.inverse_transform(synthetic_y)
    
    # Save the raw generated dataset
    df_synthetic.to_csv('GAN/synthetic_data.csv', index=False)
    print("\\nSaved filtered synthetic data to GAN/synthetic_data.csv")
    
if __name__ == '__main__':
    generate_data()
