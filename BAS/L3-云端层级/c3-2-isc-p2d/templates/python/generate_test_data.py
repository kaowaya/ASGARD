# templates/python/generate_test_data.py
import pandas as pd
import numpy as np
import os

def generate_relaxation_data(output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Generate 1 hour of data at 1S frequency (3600 points)
    n_points = 3600
    t = np.arange(0, n_points)
    
    # 1. Normal Cell (OCV=3.8, Tau=500, A=0.1, k_leak=0)
    v_normal = 3.8 - 0.1 * np.exp(-t / 500.0) + np.random.normal(0, 0.0001, n_points)
    
    # 2. ISC Cell (OCV=3.8, Tau=500, A=0.1, k_leak=2e-5 V/s)
    # 2e-5 V/s drop over 3600s = 0.072V total drop, indicating significant leakage
    v_isc = 3.8 - 0.1 * np.exp(-t / 400.0) - (2e-5 * t) + np.random.normal(0, 0.0001, n_points)
    
    # Current is physically 0 with some measurement noise
    current = np.random.normal(0, 0.01, n_points)
    
    # Combine into a single session: 
    # First 1 hour is Normal Cell relaxing
    # Then a 10 minute 'charge' pulse to break the segment
    # Then 1 hour of ISC cell relaxing
    
    df1 = pd.DataFrame({
        'timestamp': pd.date_range('2025-01-01 00:00:00', periods=n_points, freq='1s'),
        'voltage': v_normal,
        'current': current,
        'temperature': 25.0
    })
    
    df_pulse = pd.DataFrame({
        'timestamp': pd.date_range('2025-01-01 01:00:00', periods=600, freq='1s'),
        'voltage': 4.0,
        'current': 50.0, # Breaks relaxation
        'temperature': 25.5
    })
    
    df2 = pd.DataFrame({
        'timestamp': pd.date_range('2025-01-01 01:10:00', periods=n_points, freq='1s'),
        'voltage': v_isc,
        'current': current,
        'temperature': 25.0
    })
    
    final_df = pd.concat([df1, df_pulse, df2]).reset_index(drop=True)
    final_df.to_csv(output_path, index=False)
    print(f"Generated test dataset with 2 relaxation segments at: {output_path}")

if __name__ == "__main__":
    generate_relaxation_data('../../data_samples/input/synthetic_relaxation.csv')
