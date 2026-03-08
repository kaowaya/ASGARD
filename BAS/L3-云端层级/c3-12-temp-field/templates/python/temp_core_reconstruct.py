# templates/python/temp_core_reconstruct.py
"""
ASGARD C3.12 Cloud Core Temperature Field Reconstruction

Uses a two-state lumped parameter discrete thermal model to estimate the 
internal core temperature (T_core) of a battery cell using measured 
surface temperature (T_surf), ambient temperature (T_env), and current (I).

Usage:
    python temp_core_reconstruct.py --input thermal_profile.csv --output tcore.json
"""

import argparse
import pandas as pd
import numpy as np
import json
import logging
import os

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Two-State Model parameters (Mock default values for a prismatic 100Ah cell)
Cc = 800.0   # Heat capacity of core J/K
Cs = 200.0   # Heat capacity of shell/surface J/K
Rcs = 0.5    # Thermal resistance Core to Surface K/W
Rse = 1.0    # Thermal resistance Surface to Environment K/W
R_elec = 0.002 # Electrical resistance Ah Ohms for Joule heating

def estimate_t_core(df, dt_seconds=1.0):
    """
    Forward solves the discrete T_core from available T_surf and I measurements.
    Columns needed: timestamp, current, temp_surf, temp_env
    """
    req_cols = ['current', 'temp_surf', 'temp_env']
    for c in req_cols:
        if c not in df.columns:
            return {"success": False, "error": f"Missing column {c}"}
            
    i = df['current'].values
    ts = df['temp_surf'].values
    te = df['temp_env'].values
    N = len(i)
    
    t_core = np.zeros(N)
    # Initialize T_core as slightly higher than initial T_surf or equal if resting
    t_core[0] = ts[0]
    
    # Discrete explicit Euler Update
    # Q_gen = I^2 * R
    # dT_core/dt = (Q_gen - (T_core - T_surf)/Rcs) / Cc
    
    for k in range(0, N-1):
        q_gen = (i[k] ** 2) * R_elec
        heat_transfer = (t_core[k] - ts[k]) / Rcs
        
        delta_tc = (q_gen - heat_transfer) / Cc * dt_seconds
        t_core[k+1] = t_core[k] + delta_tc
        
    df['temp_core_est'] = t_core
    
    # Extract metrics
    max_tc = np.max(t_core)
    max_ts = np.max(ts)
    max_delta = np.max(t_core - ts)
    
    return {
        "success": True,
        "peak_core_temp_c": round(float(max_tc), 2),
        "peak_surf_temp_c": round(float(max_ts), 2),
        "max_temperature_gradient_c": round(float(max_delta), 2),
        "diagnostics": {
            "status": "DANGER" if max_tc > 65.0 else ("WARNING" if max_tc > 55.0 else "SAFE"),
            "core_heating_anomaly": bool(max_delta > 15.0)
        }
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        logger.warning("Input missing. Generating a 30-min 2C fast charge mock stream...")
        os.makedirs(os.path.dirname(args.input), exist_ok=True)
        # 1800 seconds (30 mins). 200A current.
        t = np.arange(1800)
        i = np.full(1800, 200.0)
        # Environment
        te = np.full(1800, 25.0)
        # Simulated slow rising surface temp up to 45C
        ts = 25.0 + 20.0 * (1.0 - np.exp(-t / 600.0))
        
        pd.DataFrame({
            'timestamp': t,
            'current': i,
            'temp_surf': ts,
            'temp_env': te
        }).to_csv(args.input, index=False)

    df = pd.read_csv(args.input)
    # Assumes 1 second dt corresponding to timestamp array
    res = estimate_t_core(df, dt_seconds=1.0)
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(res, f, indent=4)
        
    logger.info(f"C3.12 T_core evaluation complete. Peak Core T: {res.get('peak_core_temp_c')}C vs Surf: {res.get('peak_surf_temp_c')}C")

if __name__ == '__main__':
    main()
