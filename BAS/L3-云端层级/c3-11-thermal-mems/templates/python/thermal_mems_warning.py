# templates/python/thermal_mems_warning.py
"""
ASGARD C3.11 Cloud Thermal Runaway MEMS Early Warning

Applies a multi-modal rule engine against high-frequency (>=1Hz) sensor streams
from pressure (kPa), VOC gas (ppm), and NTC temps.

It checks for sudden venting signatures: dP/dt spikes + VOC gas presence.

Usage:
    python thermal_mems_warning.py --input mems_stream.csv --output tr_alarm.json
"""

import argparse
import pandas as pd
import numpy as np
import json
import logging
import os

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def evaluate_mems_saftey(df):
    """
    Checks for Thermal Runaway Venting.
    Expected columns: timestamp, pressure_kpa, voc_ppm, temp_c
    """
    req_cols = ['pressure_kpa', 'voc_ppm', 'temp_c']
    for c in req_cols:
        if c not in df.columns:
            return {"success": False, "error": f"Missing column {c}"}
            
    p = df['pressure_kpa'].values
    voc = df['voc_ppm'].values
    t = df['temp_c'].values
    
    # 1. Compute derivatives
    # Assuming 1Hz data, dt = 1s
    dp = np.diff(p, prepend=p[0])
    
    # 2. Heuristic Rules
    # Rule A: Single frame severe pressure shock (e.g. >2 kPa step) => Venting burst
    mask_shock = dp > 2.0
    
    # Rule B: Massive VOC gas + Temperature creeping
    # If VOC > 500ppm AND Temp > 60C (or sharp dT)
    mask_chem = (voc > 500.0) & (t > 60.0)
    
    is_tr_detected = np.any(mask_shock | mask_chem)
    
    if is_tr_detected:
        # Find exactly when it triggered
        idx = np.argmax(mask_shock | mask_chem)
        trigger_time = str(df['timestamp'].iloc[idx])
        return {
            "success": True,
            "alarm_status": "CRITICAL_TR",
            "trigger_time": trigger_time,
            "peak_dp": round(float(np.max(dp)), 2),
            "peak_voc": round(float(np.max(voc)), 1),
            "action": "Immediate High Voltage Cutoff recommended."
        }
    else:
        return {
            "success": True,
            "alarm_status": "SAFE",
            "peak_dp": round(float(np.max(dp)), 2),
            "peak_voc": round(float(np.max(voc)), 1)
        }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        logger.warning("Input missing. Generating a 60-second mock MEMS stream with injected Venting event...")
        os.makedirs(os.path.dirname(args.input), exist_ok=True)
        # Normal 30 secs
        p = np.full(60, 101.3) + np.random.normal(0, 0.05, 60)
        voc = np.zeros(60) + np.random.normal(5, 1, 60)
        t = np.full(60, 45.0)
        
        # At t=40, Thermal Runaway Venting occurs
        p[40:] += np.cumsum(np.append([5.0], np.random.normal(0.5, 0.1, 19))) # burst then sustained pressure
        voc[40:] += np.linspace(10, 2000, 20) # Massive gas release
        t[40:] += np.linspace(1, 30, 20) # Fast heating up to 75C
        
        pd.DataFrame({
            'timestamp': pd.date_range('2025-01-01 12:00:00', periods=60, freq='S'),
            'pressure_kpa': p,
            'voc_ppm': voc,
            'temp_c': t
        }).to_csv(args.input, index=False)

    df = pd.read_csv(args.input)
    res = evaluate_mems_saftey(df)
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(res, f, indent=4)
        
    logger.info(f"C3.11 MEMS Status: {res.get('alarm_status')}")

if __name__ == '__main__':
    main()
