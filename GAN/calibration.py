from sklearn.calibration import CalibratedClassifierCV

def calibrate_model(model, X_val, y_val, method='sigmoid'):
    """
    Applies probability calibration to a trained model.
    Method can be 'sigmoid' (Platt scaling) or 'isotonic'.
    """
    print(f"Applying {method} probability calibration...")
    calibrated_model = CalibratedClassifierCV(model, method=method, cv='prefit')
    calibrated_model.fit(X_val, y_val)
    return calibrated_model
