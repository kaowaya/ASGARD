# templates/python/svr_rv_plating.py
"""
ASGARD C3.14 Cloud Lithium Plating Detection (SV-RV Method)

Uses Symmetrical Voltage - Relaxation Voltage concepts. By matching a charge curve 
and a discharge curve at the same temperature and C-rate, it calculates the 
voltage hysteresis delta V(SOC) = V_charge(Q) - V_discharge(Q). 
Anomalous bumps in this delta curve at high SOC indicate irreversible lithium plating.

Usage:
    python svr_rv_plating.py --charge chg.csv --discharge dis.csv --output lfp_li.json
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

def estimate_sv_rv_plating(df_chg, df_dis):
    """
    Interpolates Charge and Discharge curves onto a common Depth of Charge (Ah) grid.
    Calculates Delta V.
    """
    if len(df_chg) < 100 or len(df_dis) < 100:
        return {"success": False, "error": "Insufficient data in one of the curves."}
        
    for df in [df_chg, df_dis]:
        t = pd.to_datetime(df['timestamp']).astype('int64') / 10**9
        i = df['current'].values
        # Simple Ah integration
        dt = np.gradient(t.values)
        q = np.cumsum(np.abs(i) * dt / 3600.0)
        df['capacity_ah'] = q
        
    # Align to a common capacity grid (from 0 to min_max_capacity)
    max_cap = min(df_chg['capacity_ah'].max(), df_dis['capacity_ah'].max())
    q_grid = np.linspace(0, max_cap, 500)
    
    # Must sort by capacity to interpolate properly
    df_chg = df_chg.sort_values(by='capacity_ah')
    df_dis = df_dis.sort_values(by='capacity_ah')
    
    v_chg_interp = np.interp(q_grid, df_chg['capacity_ah'].values, df_chg['voltage'].values)
    v_dis_interp = np.interp(q_grid, df_dis['capacity_ah'].values, df_dis['voltage'].values)
    
    # Calculate Hysteresis Delta V
    delta_v = v_chg_interp - v_dis_interp
    
    # Smooth Delta V
    delta_v_smooth = savgol_filter(delta_v, window_length=31, polyorder=2)
    
    # Derivative d(Delta V) / dQ
    dq = q_grid[1] - q_grid[0]
    d_delta_v = np.gradient(delta_v_smooth, dq)
    d_delta_v_smooth = savgol_filter(d_delta_v, window_length=51, polyorder=2)
    
    # In LFP, if plating occurs, d(Delta V) / dQ will show a sharp positive peak 
    # near the high SOC region (e.g. towards the right side of q_grid)
    # Search for massive peaks
    
    peaks, _ = find_peaks(d_delta_v_smooth, prominence=max(0.01, np.max(d_delta_v_smooth)*0.1))
    
    # Filter peaks that occur in the first 20% of capacity (these are usually initialization/ohmic artifacts)
    valid_peaks = [p for p in peaks if q_grid[p] > max_cap * 0.2]
    
    res_peaks = []
    for p in valid_peaks:
        res_peaks.append({
            "capacity_ah": round(float(q_grid[p]), 2),
            "delta_v": round(float(delta_v_smooth[p]), 3),
            "derivative_intensity": round(float(d_delta_v_smooth[p]), 3)
        })
        
    status = "PLATING_DETECTED" if len(valid_peaks) > 0 else "HEALTHY"
    
    return {
        "success": True,
        "max_aligned_cap_ah": round(max_cap, 2),
        "status": status,
        "anomaly_peaks": res_peaks
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--charge', required=True)
    parser.add_argument('--discharge', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    if not os.path.exists(args.charge):
        logger.warning("Mock data missing. Generating matched SV-RV LFP curves...")
        os.makedirs(os.path.dirname(args.charge), exist_ok=True)
        
        t = np.arange(3600)
        # Mock capacity 0 to 100 Ah
        q = np.linspace(0, 100, 3600)
        
        # Base LFP OCV is very flat
        ocv = 3.2 + 0.1 * (q/100.0) + 0.2 * np.exp(-10 * (1 - q/100.0))
        
        # Charge has positive polarization. 
        # Introduce a Plating bump polarization at q > 80Ah
        bump = 0.05 * np.exp(-((q - 85) / 5)**2)
        v_c = ocv + 0.05 + bump
        pd.DataFrame({'timestamp': pd.date_range('2025', periods=3600, freq='S'), 'current': 100.0, 'voltage': v_c}).to_csv(args.charge, index=False)
        
        # Discharge has negative polarization
        v_d = ocv - 0.05
        pd.DataFrame({'timestamp': pd.date_range('2025-02', periods=3600, freq='S'), 'current': -100.0, 'voltage': v_d}).to_csv(args.discharge, index=False)

    df_c = pd.read_csv(args.charge)
    df_d = pd.read_csv(args.discharge)
    res = estimate_sv_rv_plating(df_c, df_d)
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(res, f, indent=4)
        
    logger.info(f"C3.14 Plating SV-RV Exam complete. Result: {res.get('status')}")

if __name__ == '__main__':
    main()
