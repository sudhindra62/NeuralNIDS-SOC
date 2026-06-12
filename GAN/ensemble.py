import numpy as np

class WeightedEnsemble:
    def __init__(self, model_orig, model_phase2, weight_orig=0.6, weight_phase2=0.4):
        self.model_orig = model_orig
        self.model_phase2 = model_phase2
        self.weight_orig = weight_orig
        self.weight_phase2 = weight_phase2

    def predict_proba(self, X):
        """
        Returns weighted averaged probabilities: 0.6*Orig + 0.4*Phase2
        """
        # Ensure X is DataFrame for XGBoost if needed, but here we assume it's scaled numpy or DF
        probs_orig = self.model_orig.predict_proba(X)
        probs_phase2 = self.model_phase2.predict_proba(X)
        
        final_probs = (self.weight_orig * probs_orig) + (self.weight_phase2 * probs_phase2)
        return final_probs

    def predict(self, X):
        """
        Default prediction based on weighted argmax
        """
        probs = self.predict_proba(X)
        return np.argmax(probs, axis=1)
