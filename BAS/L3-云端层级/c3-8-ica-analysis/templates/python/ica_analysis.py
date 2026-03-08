# templates/python/ica_analysis.py
"""
ASGARD C3.8 Cloud Incremental Capacity Analysis (ICA dQ/dV)

Processes constant current (CC) charging data.
Extracts dQ/dV features by applying severe smoothing (Savitzky-Golay) 
and isolates peak voltages indicating specific electrochemical phase transitions.

Usage:
    python ica_analysis.py --input cc_charge.csv --output ica_peaks.json
"""

import argparse
import pandas as pd
import numpy as np
import json
import logging
import os
from scipy.signal import savgol_filter, find_peaks

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def perform_ica(df, voltage_col='voltage', current_col='current', time_col='timestamp'):
    """
    Analyzes the charging DataFrame to extract dQ/dV peaks.
    Assuming the dataframe is already sorted by time and is a continuous charging chunk.
    """
    if len(df) < 100:
        return {"success": False, "error": "Insufficient data length for ICA."}

    # Ensure time is in seconds
    if not np.issubdtype(df[time_col].dtype, np.number):
        t_sec = pd.to_datetime(df[time_col]).astype('int64') / 10**9
    else:
        t_sec = df[time_col]
        
    t_sec = t_sec.values
    v = df[voltage_col].values
    i = df[current_col].values
    
    # Calculate Capacity Q (Ah)
    dt = np.diff(t_sec, prepend=t_sec[0])
    dq_ah = (i * dt) / 3600.0
    q = np.cumsum(dq_ah)
    
    # 1. Sort by voltage to ensure monotonic increasing V (strictly needed for dQ/dV)
    sort_idx = np.argsort(v)
    v_sorted = v[sort_idx]
    q_sorted = q[sort_idx]
    
    # 2. Resample onto an evenly spaced voltage grid to avoid dV=0 divisions
    v_grid = np.linspace(v_sorted.min(), v_sorted.max(), 500)
    q_grid = np.interp(v_grid, v_sorted, q_sorted)
    
    # 3. Apply Savitzky-Golay Filter on Q(V) before differentiation
    # window length depends on noise. using a relatively large window for robust cloud pipelines.
    q_smooth = savgol_filter(q_grid, window_length=51, polyorder=3)
    
    # 4. Differentiation dQ/dV
    dv = v_grid[1] - v_grid[0]
    dqdv = np.gradient(q_smooth, dv)
    
    # 5. Smooth the derivative again
    dqdv_smooth = savgol_filter(dqdv, window_length=31, polyorder=2)
    
    # 6. Peak Finding
    # Prominence parameter avoids finding tiny ripple peaks
    peaks, properties = find_peaks(dqdv_smooth, prominence=max(dqdv_smooth)*0.1, distance=20)
    
    peak_results = []
    for i, p in enumerate(peaks):
        peak_results.append({
            "peak_id": i + 1,
            "voltage_v": round(float(v_grid[p]), 3),
            "dqdv_intensity": round(float(dqdv_smooth[p]), 3)
        })
        
    return {
        "success": True,
        "processed_points": len(v_grid),
        "peaks_detected": len(peaks),
        "peak_details": peak_results
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        logger.warning("Input missing. Generating a mock Constant Current charging sequence...")
        os.makedirs(os.path.dirname(args.input), exist_ok=True)
        t = np.arange(0, 3600, 1) # 1 hour charge
        # Emulate phase transition steps in voltage
        # Ideal V curve has plateaus which create peaks in dQ/dV
        v = 3.0 + 1.2 * (t / 3600)**0.8 + 0.05 * np.sin(t/500)
        # Add random noise
        v += np.random.normal(0, 0.001, len(v))
        i = np.full(len(t), 100.0) # 100A constant charge
        pd.DataFrame({'timestamp': t, 'voltage': v, 'current': i}).to_csv(args.input, index=False)

    df = pd.read_csv(args.input)
    res = perform_ica(df)
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(res, f, indent=4)
        
    logger.info(f"C3.8 ICA extracted {res.get('peaks_detected', 0)} electrochemistry peaks.")

if __name__ == '__main__':
    main()
