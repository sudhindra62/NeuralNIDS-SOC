import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from xgboost import XGBClassifier
from tensorflow.keras.models import load_model

def create_report_v2_notebook():
    cells = []
    
    # Title
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": ["# GAN Augmentation Phase 2: Refined & Calibrated Evaluation\n\n",
                   "This report compares the Phase 1 results against the Phase 2 improvements (Statistical Filtering, Sample Weighting, and Probability Calibration)."]
    })
    
    eval_code = """import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
from xgboost import XGBClassifier
from tensorflow.keras.models import load_model

# 1. Load Data
real_df = pd.read_csv('../ml_training/dataset/unsw_nb_cleaned.csv')
features = ['proto', 'state', 'dur', 'spkts', 'dpkts', 'sbytes', 'dbytes', 'sttl', 'dttl', 'sload', 'dload', 'sloss', 'dloss', 'ct_srv_src', 'ct_dst_ltm']

# Recreate test set (same split as previous)
X_real = real_df[features].copy()
y_real = real_df['attack_cat'].copy()
X_train, X_test, y_train, y_test = train_test_split(X_real, y_real, test_size=0.15, random_state=42, stratify=y_real)

# Preprocess
le_dict = {}
for c in ['proto', 'state']:
    le = LabelEncoder()
    le.fit(X_train[c].astype(str))
    X_test.loc[:, c] = X_test[c].map(lambda s: le.transform([s])[0] if s in le.classes_ else -1)

scaler = joblib.load('../ml_training/artifacts_improved/scaler.pkl')
label_encoder = joblib.load('../ml_training/artifacts_improved/label_encoder.pkl')
X_test_scaled = scaler.transform(X_test)
y_test_enc = label_encoder.transform(y_test)
classes = label_encoder.classes_

# 2. Load All Models
print("Loading models...")
# XGBoost Versions
xgb_orig = XGBClassifier()
xgb_orig.load_model('finetune/xgboost_original.json')

xgb_v1 = XGBClassifier()
xgb_v1.load_model('finetune/xgboost_finetuned.model')

xgb_v2 = joblib.load('finetune_v2/xgboost_finetuned_v2.pkl')

# CNN-LSTM Versions
cnn_v1 = load_model('finetune/cnn_lstm_finetuned.keras')
cnn_v2 = load_model('finetune_v2/cnn_lstm_finetuned_v2.keras')

# 3. Evaluation Function
def evaluate(model, X, y, name, is_keras=False):
    if is_keras:
        X_seq = np.expand_dims(X, axis=1)
        y_pred = np.argmax(model.predict(X_seq, verbose=0), axis=1)
    else:
        y_pred = model.predict(X)
    
    acc = accuracy_score(y, y_pred)
    f1 = f1_score(y, y_pred, average='macro')
    return y_pred, acc, f1

# Run Predictions
y_p_xgb0, acc0, f10 = evaluate(xgb_orig, X_test_scaled, y_test_enc, "XGB Original")
y_p_xgb1, acc1, f11 = evaluate(xgb_v1, X_test_scaled, y_test_enc, "XGB Phase 1")
y_p_xgb2, acc2, f12 = evaluate(xgb_v2, X_test_scaled, y_test_enc, "XGB Phase 2")
y_p_cnn1, acc_c1, f1_c1 = evaluate(cnn_v1, X_test_scaled, y_test_enc, "CNN Phase 1", True)
y_p_cnn2, acc_c2, f1_c2 = evaluate(cnn_v2, X_test_scaled, y_test_enc, "CNN Phase 2", True)

# Display Summary Table
summary = pd.DataFrame({
    'Model': ['XGB Original', 'XGB Phase 1', 'XGB Phase 2', 'CNN Phase 1', 'CNN Phase 2'],
    'Accuracy': [acc0, acc1, acc2, acc_c1, acc_c2],
    'Macro F1': [f10, f11, f12, f1_c1, f1_c2]
})
print("\\nComparison Summary:")
print(summary)

print("\\nPhase 2 Detailed Report (XGBoost):")
print(classification_report(y_test_enc, y_p_xgb2, target_names=classes))
"""
    cells.append({
        "cell_type": "code",
        "execution_count": 1,
        "metadata": {},
        "outputs": [],
        "source": [eval_code]
    })
    
    cm_code = """# Confusion Matrix Comparison (Phase 1 vs Phase 2)
fig, axes = plt.subplots(2, 2, figsize=(20, 16))

# XGB Phase 1
sns.heatmap(confusion_matrix(y_test_enc, y_p_xgb1), annot=True, fmt='d', cmap='Blues', ax=axes[0,0], xticklabels=classes, yticklabels=classes)
axes[0,0].set_title('XGBoost Phase 1')

# XGB Phase 2
sns.heatmap(confusion_matrix(y_test_enc, y_p_xgb2), annot=True, fmt='d', cmap='Greens', ax=axes[0,1], xticklabels=classes, yticklabels=classes)
axes[0,1].set_title('XGBoost Phase 2 (Refined & Calibrated)')

# CNN Phase 1
sns.heatmap(confusion_matrix(y_test_enc, y_p_cnn1), annot=True, fmt='d', cmap='Oranges', ax=axes[1,0], xticklabels=classes, yticklabels=classes)
axes[1,0].set_title('CNN-LSTM Phase 1')

# CNN Phase 2
sns.heatmap(confusion_matrix(y_test_enc, y_p_cnn2), annot=True, fmt='d', cmap='Purples', ax=axes[1,1], xticklabels=classes, yticklabels=classes)
axes[1,1].set_title('CNN-LSTM Phase 2 (Stabilized)')

plt.tight_layout()
plt.show()
"""
    cells.append({
        "cell_type": "code",
        "execution_count": 2,
        "metadata": {},
        "outputs": [],
        "source": [cm_code]
    })
    
    nb = {
        "cells": cells,
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5
    }
    with open('GAN/report_v2.ipynb', 'w') as f:
        json.dump(nb, f, indent=1)
    print("Notebook GAN/report_v2.ipynb created.")

def create_report_v3_notebook():
    cells = []
    
    # Title
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": ["# GAN Augmentation Phase 3: Decision-Level Optimization\n\n",
                   "This report evaluates the Weighted Ensemble (Original + Phase 2) and Per-Class Threshold Tuning."]
    })
    
    eval_code = """import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
from xgboost import XGBClassifier
from ensemble import WeightedEnsemble
from threshold_tuning import ThresholdTuner

# 1. Load Data
real_df = pd.read_csv('../ml_training/dataset/unsw_nb_cleaned.csv')
features = ['proto', 'state', 'dur', 'spkts', 'dpkts', 'sbytes', 'dbytes', 'sttl', 'dttl', 'sload', 'dload', 'sloss', 'dloss', 'ct_srv_src', 'ct_dst_ltm']

# Recreate test set
X_real = real_df[features].copy()
y_real = real_df['attack_cat'].copy()
X_train, X_test, y_train, y_test = train_test_split(X_real, y_real, test_size=0.15, random_state=42, stratify=y_real)

# Preprocess
le_dict = {}
for c in ['proto', 'state']:
    le = LabelEncoder()
    le.fit(X_train[c].astype(str))
    X_test.loc[:, c] = X_test[c].map(lambda s: le.transform([s])[0] if s in le.classes_ else -1)

scaler = joblib.load('../ml_training/artifacts_improved/scaler.pkl')
label_encoder = joblib.load('../ml_training/artifacts_improved/label_encoder.pkl')
X_test_scaled = scaler.transform(X_test)
y_test_enc = label_encoder.transform(y_test)
classes = label_encoder.classes_

# 2. Load Models
xgb_orig = XGBClassifier()
xgb_orig.load_model('finetune/xgboost_original.json')

xgb_v2 = joblib.load('finetune_v2/xgboost_finetuned_v2.pkl')

# Initialize Ensemble
ensemble = WeightedEnsemble(xgb_orig, xgb_v2, weight_orig=0.6, weight_phase2=0.4)

# 3. Threshold Tuning (Using same logic as in run_phase_3)
target_classes = ['Analysis', 'Backdoor', 'Shellcode']
target_indices = [label_encoder.transform([c])[0] for c in target_classes]
tuner = ThresholdTuner(target_indices)

# We use the test set for the final report display
probs_ensemble = ensemble.predict_proba(X_test_scaled)

# Load tuned thresholds (assuming run_phase_3 saved them)
try:
    tuner.thresholds = joblib.load('finetune_v2/optimal_thresholds.pkl')
    print("Loaded optimal thresholds:", tuner.thresholds)
except:
    print("Optimal thresholds not found, using default 0.5")

# 4. Predict
y_pred_orig = xgb_orig.predict(X_test_scaled)
y_pred_v2 = xgb_v2.predict(X_test_scaled)
y_pred_ens = ensemble.predict(X_test_scaled)
y_pred_tuned = tuner.predict_with_thresholds(probs_ensemble)

# Summary
def get_metrics(y_true, y_pred, name):
    return {
        'Model': name,
        'Accuracy': accuracy_score(y_true, y_pred),
        'Macro F1': f1_score(y_true, y_pred, average='macro')
    }

results = [
    get_metrics(y_test_enc, y_pred_orig, "XGB Original"),
    get_metrics(y_test_enc, y_pred_v2, "XGB Phase 2"),
    get_metrics(y_test_enc, y_pred_ens, "Weighted Ensemble"),
    get_metrics(y_test_enc, y_pred_tuned, "Ensemble + Threshold Tuning")
]
summary_df = pd.DataFrame(results)
print("\\nComparison Summary:")
print(summary_df)

print("\\nPhase 3 Optimized Model Report:")
print(classification_report(y_test_enc, y_pred_tuned, target_names=classes))
"""
    cells.append({
        "cell_type": "code",
        "execution_count": 1,
        "metadata": {},
        "outputs": [],
        "source": [eval_code]
    })
    
    cm_code = """# Confusion Matrix Comparison (Phase 2 vs Phase 3)
fig, axes = plt.subplots(1, 2, figsize=(20, 8))

# Phase 2
sns.heatmap(confusion_matrix(y_test_enc, y_pred_v2), annot=True, fmt='d', cmap='Greens', ax=axes[0], xticklabels=classes, yticklabels=classes)
axes[0].set_title('Phase 2 XGBoost (GAN)')

# Phase 3
sns.heatmap(confusion_matrix(y_test_enc, y_pred_tuned), annot=True, fmt='d', cmap='Purples', ax=axes[1], xticklabels=classes, yticklabels=classes)
axes[1].set_title('Phase 3 Ensemble + Threshold Tuning')

plt.tight_layout()
plt.show()
"""
    cells.append({
        "cell_type": "code",
        "execution_count": 2,
        "metadata": {},
        "outputs": [],
        "source": [cm_code]
    })
    
    nb = {
        "cells": cells,
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5
    }
    with open('GAN/report_v3.ipynb', 'w') as f:
        json.dump(nb, f, indent=1)
    print("Notebook GAN/report_v3.ipynb created.")

def run_phase_3():
    print("Step 1: Loading Models & Data for Decision Optimization...")
    import joblib
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder
    from xgboost import XGBClassifier
    from ensemble import WeightedEnsemble
    from threshold_tuning import ThresholdTuner
    
    real_df = pd.read_csv('ml_training/dataset/unsw_nb_cleaned.csv')
    features = ['proto', 'state', 'dur', 'spkts', 'dpkts', 'sbytes', 'dbytes', 'sttl', 'dttl', 'sload', 'dload', 'sloss', 'dloss', 'ct_srv_src', 'ct_dst_ltm']
    X_real = real_df[features].copy()
    y_real = real_df['attack_cat'].copy()
    
    # We need a validation set for tuning thresholds (using the training split part)
    X_train_full, X_test, y_train_full, y_test = train_test_split(X_real, y_real, test_size=0.15, random_state=42, stratify=y_real)
    X_train, X_val, y_train, y_val = train_test_split(X_train_full, y_train_full, test_size=0.1, random_state=42, stratify=y_train_full)
    
    # Preprocess Val
    for c in ['proto', 'state']:
        le = LabelEncoder()
        le.fit(X_train[c].astype(str))
        X_val.loc[:, c] = X_val[c].map(lambda s: le.transform([s])[0] if s in le.classes_ else -1)
        
    scaler = joblib.load('ml_training/artifacts_improved/scaler.pkl')
    label_encoder = joblib.load('ml_training/artifacts_improved/label_encoder.pkl')
    X_val_scaled = scaler.transform(X_val)
    y_val_enc = label_encoder.transform(y_val)
    
    # Load Models
    xgb_orig = XGBClassifier()
    xgb_orig.load_model('GAN/finetune/xgboost_original.json')
    xgb_v2 = joblib.load('GAN/finetune_v2/xgboost_finetuned_v2.pkl')
    
    # Initialize Ensemble
    ensemble = WeightedEnsemble(xgb_orig, xgb_v2)
    
    print("\\nStep 2: Tuning Thresholds on Validation Set...")
    target_classes = ['Analysis', 'Backdoor', 'Shellcode']
    target_indices = [label_encoder.transform([c])[0] for c in target_classes]
    tuner = ThresholdTuner(target_indices)
    
    probs_val = ensemble.predict_proba(X_val_scaled)
    tuner.tune(probs_val, y_val_enc)
    
    # Save thresholds
    joblib.dump(tuner.thresholds, 'GAN/finetune_v2/optimal_thresholds.pkl')
    
    print("\\nStep 3: Generating Phase 3 Report...")
    create_report_v3_notebook()
    
    print("\\nPhase 3 Completed Successfully.")

if __name__ == '__main__':
    # run_phase_2() # Phase 2 already done
    run_phase_3()
