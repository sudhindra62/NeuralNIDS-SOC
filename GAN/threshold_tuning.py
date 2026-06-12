import numpy as np
from sklearn.metrics import f1_score

class ThresholdTuner:
    def __init__(self, target_classes_indices):
        self.target_classes_indices = target_classes_indices
        self.thresholds = {idx: 0.5 for idx in target_classes_indices}

    def tune(self, probs, y_true):
        """
        Sweeps thresholds from 0.1 to 0.5 to find optimal F1 for each target class.
        """
        print("Tuning thresholds for minority classes...")
        for idx in self.target_classes_indices:
            best_f1 = -1
            best_t = 0.5
            
            for t in np.arange(0.1, 0.55, 0.05):
                # Apply threshold t for current class idx
                # If prob[idx] > t, predict idx, else use current argmax
                y_pred = np.argmax(probs, axis=1)
                mask = probs[:, idx] > t
                y_pred[mask] = idx
                
                score = f1_score(y_true, y_pred, average='macro')
                
                # We optimize for Macro F1 overall, which improves when minority recall improves without killing precision
                if score > best_f1:
                    best_f1 = score
                    best_t = t
            
            self.thresholds[idx] = best_t
            print(f"  Class Index {idx}: Optimal Threshold = {best_t:.2f} (Macro F1: {best_f1:.4f})")

    def predict_with_thresholds(self, probs):
        """
        Applies tuned thresholds to probabilities.
        Minority classes take precedence if they exceed their threshold.
        """
        y_pred = np.argmax(probs, axis=1)
        
        # Apply in reverse order of 'rarity' or importance if needed, 
        # but here we just check if any target class exceeds its threshold.
        # We sort by lowest threshold first to give 'most sensitive' classes a chance.
        sorted_indices = sorted(self.thresholds.keys(), key=lambda x: self.thresholds[x])
        
        for idx in sorted_indices:
            t = self.thresholds[idx]
            mask = probs[:, idx] > t
            y_pred[mask] = idx
            
        return y_pred
