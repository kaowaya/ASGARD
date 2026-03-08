# templates/python/lithium_plating_relax.py
"""
ASGARD C3.13 Cloud Lithium Plating Detection (Relaxation Method)

Analyzes the voltage relaxation curve immediately following a fast charge event.
Searches for a local minimum/plateau in the dV/dt curve, which represents 
the stripping of plated metallic lithium from the anode surface.

Usage:
    python lithium_plating_relax.py --input post_charge_rest.csv --output li_report.json
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

def detect_lithium_plating(df, time_col='timestamp', volt_col='voltage'):
    """
    Detects the stripping plateau in relaxation voltage.
    """
    if len(df) < 300: # Need decent rest length (e.g. 5+ mins at 1Hz)
        return {"success": False, "error": "Insufficient relaxation data length."}

    # Ensure time is in seconds
    if not np.issubdtype(df[time_col].dtype, np.number):
        t_sec = pd.to_datetime(df[time_col]).astype('int64') / 10**9
    else:
        t_sec = df[time_col].values
        
    t_sec = t_sec - t_sec[0] # Zero start
    v = df[volt_col].values
    
    # Smooth Voltage (V)
    v_smooth = savgol_filter(v, window_length=51, polyorder=3)
    
    # Calculate dV/dt (Should be negative as voltage is dropping)
    dt = np.gradient(t_sec)
    dvdt = np.gradient(v_smooth, t_sec)
    
    # Smooth dV/dt heavily to find macro inflection points
    dvdt_smooth = savgol_filter(dvdt, window_length=151, polyorder=2)
    
    # A normal battery's dV/dt starts highly negative and monotonically approaches 0
    # A plated battery's dV/dt starts negative, holds at a plateau (less negative), 
    # then drops AGAIN (more negative) when stripping finishes, before finally approaching 0.
    # Therefore, we look for a local MINIMUM in dV/dt (the secondary drop).
    
    # Invert dvdt to use find_peaks (which finds local maxima)
    # We want to find the valley in the negative dV/dt curve.
    inv_dvdt = -dvdt_smooth
    
    # Find peaks in the inverted signal (valleys in original)
    peaks, props = find_peaks(inv_dvdt, prominence=np.max(np.abs(dvdt_smooth))*0.15, distance=60)
    
    has_plating = len(peaks) > 0
    
    diagnostics = []
    if has_plating:
        for p in peaks:
            diagnostics.append({
                "stripping_end_time_s": float(t_sec[p]),
                "stripping_voltage_v": float(v_smooth[p]),
                "intensity_dvdt": float(dvdt_smooth[p])
            })
            
    # Require stripping plateau to occur after the primary concentration polarization settles (120s)
    # AND require the plateau inflection intensity to be significant (filtering out micro-noise < 1e-5 V/s)
    valid_peaks = [d for d in diagnostics if d["stripping_end_time_s"] > 120.0 and d["intensity_dvdt"] < -3.0e-5]
    
    return {
        "success": True,
        "has_lithium_plating": len(valid_peaks) > 0,
        "plating_events": valid_peaks,
        "status": "DANGER" if len(valid_peaks) > 0 else "HEALTHY"
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        logger.warning("Input missing. Generating a 3600s mock relaxation with a hidden Lithium stripping plateau...")
        os.makedirs(os.path.dirname(args.input), exist_ok=True)
        
        t = np.arange(3600.0)
        # Normal exponential decay
        v = 4.1 + 0.1 * np.exp(-t / 500.0)
        
        # Inject Lithium Plating Stripping Plateau
        # Between t=300s and t=800s, the voltage is "held up" by the stripping reaction
        # We simulate this by superimposing a gaussian bump
        plateau = 0.005 * np.exp(-((t - 500) / 200)**2)
        v += plateau
        # Add slight noise
        v += np.random.normal(0, 0.0001, len(t))
        
        pd.DataFrame({'timestamp': t, 'voltage': v}).to_csv(args.input, index=False)

    df = pd.read_csv(args.input)
    res = detect_lithium_plating(df)
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(res, f, indent=4)
        
    logger.info(f"C3.13 Lithium Plating Exam complete. Result: {res.get('status')} | Found {len(res.get('plating_events', []))} stripping signatures.")

if __name__ == '__main__':
    main()
