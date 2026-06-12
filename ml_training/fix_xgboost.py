import pandas as pd
import numpy as np
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import accuracy_score

print("Loading data...")
df = pd.read_csv('dataset/unsw_nb_cleaned.csv')

features = ['proto', 'state', 'dur', 'spkts', 'dpkts', 'sbytes', 'dbytes', 'sttl', 'dttl', 'sload', 'dload', 'sloss', 'dloss', 'ct_srv_src', 'ct_dst_ltm']
X = df[features].copy()
y = df['attack_cat'].copy()

print("Loading preprocessor and encoder...")
preprocessor = joblib.load('artifacts/preprocessor.pkl')
label_encoder = joblib.load('artifacts/label_encoder.pkl')

print("Preprocessing...")
X_encoded = preprocessor.transform(X).astype(np.float32)
y_encoded = label_encoder.transform(y)

X_train, X_test, y_train, y_test = train_test_split(X_encoded, y_encoded, test_size=0.15, random_state=42, stratify=y_encoded)

print("Computing weights...")
classes = np.unique(y_train)
class_weights = compute_class_weight(class_weight='balanced', classes=classes, y=y_train)

sample_weights = np.zeros(len(y_train))
for i in range(len(classes)):
    sample_weights[y_train == i] = class_weights[i]

print("Training XGBoost...")
model_xgb = XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    tree_method='hist'
)
model_xgb.fit(X_train, y_train, sample_weight=sample_weights)

preds = model_xgb.predict(X_test)
print("Accuracy:", accuracy_score(y_test, preds))

print("Saving fixed model...")
model_xgb.save_model('artifacts/xgboost_improved_model.json')
print("Done!")
