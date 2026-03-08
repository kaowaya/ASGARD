# templates/python/eis_analysis.py
"""
ASGARD C3.9 Cloud EIS DRT Analysis

Converts Electrochemical Impedance Spectroscopy (EIS) frequency-domain data 
into a Distribution of Relaxation Times (DRT) to separate and identify 
polarization effects (e.g., SEI layer vs Charge Transfer).

Usage:
    python eis_analysis.py --input online_eis.csv --output drt_report.json
"""

import argparse
import pandas as pd
import numpy as np
import json
import logging
import os
from scipy.optimize import minimize

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def compute_drt(df, lambda_reg=1e-3):
    """
    Simplified DRT Computation via Tikhonov Regularization (Ridge Regression)
    Fits Z_imaginary to the DRT integral.
    """
    if 'freq_hz' not in df.columns or 'z_imag' not in df.columns:
        return {"success": False, "error": "Missing freq_hz or z_imag columns."}

    freqs = df['freq_hz'].values
    z_im = df['z_imag'].values  # Typically negative for capacitive loops
    
    # Check if we have valid data
    if len(freqs) < 10:
        return {"success": False, "error": "Not enough EIS frequencies."}

    # Discretize tau (Relaxation time range based on frequencies)
    tau_min = 1.0 / (2 * np.pi * freqs.max()) * 0.1
    tau_max = 1.0 / (2 * np.pi * freqs.min()) * 10.0
    N_tau = 100
    taus = np.logspace(np.log10(tau_min), np.log10(tau_max), N_tau)
    
    # Construct Design Matrix A for Z_imag
    # Z_im(f) = sum_k [ - (w * tau_k) / (1 + (w * tau_k)^2) * G_k ]
    omega = 2 * np.pi * freqs
    Omega, Tau = np.meshgrid(omega, taus, indexing='ij')
    
    A_im = - (Omega * Tau) / (1.0 + (Omega * Tau)**2)
    
    # Objective function: ||A*x - Z_im||^2 + lambda * ||L*x||^2
    # We use a simple L2 norm on X for regularization (zero-order Tikhonov)
    
    def objective(x):
        residual = A_im.dot(x) - z_im
        reg = lambda_reg * np.sum(x**2)
        return np.sum(residual**2) + reg
        
    # Positivity constraint: DRT spectrum G(tau) must be >= 0
    bounds = [(0, None) for _ in range(N_tau)]
    x0 = np.ones(N_tau) * 0.01
    
    logger.info("Solving ill-posed DRT inversion...")
    res = minimize(objective, x0, bounds=bounds, method='L-BFGS-B')
    
    if not res.success:
        return {"success": False, "error": "DRT optimizer failed to converge."}
        
    g_tau = res.x
    
    # Feature Extraction (Area under curve in different regions)
    # Region 1: SEI (tau < 0.01)
    # Region 2: Charge Transfer (0.01 < tau < 1.0)
    # Region 3: Diffusion (tau > 1.0)
    mask_sei = taus < 0.01
    mask_ct = (taus >= 0.01) & (taus < 1.0)
    mask_diff = taus >= 1.0
    
    r_sei = np.trapz(g_tau[mask_sei], np.log(taus[mask_sei])) if mask_sei.any() else 0.0
    r_ct = np.trapz(g_tau[mask_ct], np.log(taus[mask_ct])) if mask_ct.any() else 0.0
    r_diff = np.trapz(g_tau[mask_diff], np.log(taus[mask_diff])) if mask_diff.any() else 0.0

    peaks = []
    # simple peak finder in G(tau)
    from scipy.signal import find_peaks
    p_idx, _ = find_peaks(g_tau, prominence=np.max(g_tau)*0.05)
    for p in p_idx:
        peaks.append({
            "tau_s": float(taus[p]),
            "freq_hz": float(1.0 / (2 * np.pi * taus[p])),
            "intensity": float(g_tau[p])
        })
        
    return {
        "success": True,
        "features_ohm": {
            "R_sei": round(max(0, r_sei), 6),
            "R_ct": round(max(0, r_ct), 6),
            "R_diff": round(max(0, r_diff), 6)
        },
        "peaks_detected": len(peaks),
        "peak_details": peaks
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        logger.warning("Input missing. Generating a Mock Nyquist EIS data set...")
        os.makedirs(os.path.dirname(args.input), exist_ok=True)
        # Mock frequency range 1kHZ to 0.01Hz
        f = np.logspace(3, -2, 60)
        w = 2 * np.pi * f
        # Mock 2-RC circuit + Series R
        R_s, R1, C1, R2, C2 = 0.05, 0.015, 0.1, 0.025, 2.0
        Z = R_s + R1/(1 + 1j*w*R1*C1) + R2/(1 + 1j*w*R2*C2)
        
        pd.DataFrame({
            'freq_hz': f,
            'z_real': Z.real,
            'z_imag': Z.imag
        }).to_csv(args.input, index=False)

    df = pd.read_csv(args.input)
    res = compute_drt(df)
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(res, f, indent=4)
        
    if res.get('success'):
        feats = res['features_ohm']
        logger.info(f"C3.9 DRT Analysis complete. SEI:{feats['R_sei']} CT:{feats['R_ct']} Diff:{feats['R_diff']}")
    else:
        logger.error(f"Failed: {res.get('error')}")

if __name__ == '__main__':
    main()
