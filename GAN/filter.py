import pandas as pd
import numpy as np

def run_filter():
    print("Loading datasets for filtering...")
    real_df = pd.read_csv('ml_training/dataset/unsw_nb_cleaned.csv')
    synth_df = pd.read_csv('GAN/synthetic_data.csv')
    
    # Define features and target classes
    features = ['proto', 'state', 'dur', 'spkts', 'dpkts', 'sbytes', 'dbytes', 
                'sttl', 'dttl', 'sload', 'dload', 'sloss', 'dloss', 'ct_srv_src', 'ct_dst_ltm']
    
    target_classes = ['Analysis', 'Backdoor', 'Shellcode', 'Worms']
    
    refined_samples = []
    
    print("Filtering synthetic samples based on Real Data Mean +/- 2*Std...")
    
    for cls in target_classes:
        # Get real data for this class
        real_cls_data = real_df[real_df['attack_cat'] == cls][features].copy()
        
        # Get synthetic data for this class
        synth_cls_data = synth_df[synth_df['attack_cat'] == cls].copy()
        
        if synth_cls_data.empty:
            continue
            
        print(f"\nProcessing class: {cls}")
        print(f"Original synthetic samples: {len(synth_cls_data)}")
        
        # Calculate mean and std on continuous real data
        continuous_features = [f for f in features if f not in ['proto', 'state']]
        mean_vals = real_cls_data[continuous_features].mean()
        std_vals = real_cls_data[continuous_features].std()
        
        std_vals = std_vals.replace(0, 1e-6)
        
        # Create bounds
        lower_bound = mean_vals - 2 * std_vals
        upper_bound = mean_vals + 2 * std_vals
        
        mask = pd.Series(True, index=synth_cls_data.index)
        
        for f in continuous_features:
            f_mask = (synth_cls_data[f] >= lower_bound[f]) & (synth_cls_data[f] <= upper_bound[f])
            mask = mask & f_mask
            
        filtered_cls_data = synth_cls_data[mask]
        print(f"Filtered synthetic samples (retained): {len(filtered_cls_data)}")
        
        refined_samples.append(filtered_cls_data)
        
    if refined_samples:
        refined_df = pd.concat(refined_samples, ignore_index=True)
        refined_df.to_csv('GAN/refined_synthetic_data.csv', index=False)
        print(f"\nSuccessfully saved {len(refined_df)} refined samples to GAN/refined_synthetic_data.csv")
    else:
        print("\nWarning: No synthetic samples passed the strict filtering criteria.")

if __name__ == '__main__':
    run_filter()
