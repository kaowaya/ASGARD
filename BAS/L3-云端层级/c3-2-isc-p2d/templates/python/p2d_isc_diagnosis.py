# templates/python/p2d_isc_diagnosis.py
"""
ASGARD L3-Cloud P2D/SPM Internal Short Circuit (ISC) Diagnostics

This module performs cloud-level ISC detection by extracting relaxation periods (I=0)
from pre-processed time-series data and fitting a reduced-order electrochemical 
Single Particle Model (SPM) with a leakage term.

Model equation:
V_relax(t) = OCV_t0 - A * exp(-t / tau_d) - k_leak * t

A persistent positive k_leak parameter indicates a parasitic leakage current (ISC).

Usage:
    python p2d_isc_diagnosis.py --input clean_features.csv --output isc_report.json
"""

import argparse
import logging
import json
import os
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class P2dIscDiagnostics:
    def __init__(self, current_threshold=0.1, min_relax_seconds=1800, leakage_warn_threshold_v_s=2e-8):
        """
        Args:
            current_threshold: The maximum absolute current to be considered "resting" (A).
            min_relax_seconds: Minimum duration of the relaxation period to perform a fit (s).
            leakage_warn_threshold_v_s: The threshold for k_leak (V/s) above which an ISC warning is generated.
        """
        self.current_threshold = current_threshold
        self.min_relax_sec = min_relax_seconds
        self.leakage_thresh = leakage_warn_threshold_v_s

    @staticmethod
    def _relaxation_model(t, ocv_t0, a, tau_d, k_leak):
        """
        Reduced-order electrochemical relaxation function.
        t: time array (seconds since relaxation started)
        ocv_t0: Initial resting voltage (V)
        a: Amplitude of solid-phase diffusion polarization (V)
        tau_d: Solid-phase diffusion time constant (s)
        k_leak: Voltage leakage rate due to internal short (V/s)
        """
        return ocv_t0 - a * np.exp(-t / tau_d) - k_leak * t

    def extract_relaxation_segments(self, df):
        """Finds contiguous periods where |current| < threshold for >= min_relax_sec."""
        # Create a boolean mask where current is practically zero
        resting_mask = df['current'].abs() <= self.current_threshold
        
        # Identify contiguous blocks (segments) of resting state
        # A shift in the mask indicates a state change
        segment_id = (resting_mask != resting_mask.shift()).cumsum()
        
        segments = []
        for sid, group in df[resting_mask].groupby(segment_id):
            duration = (group['timestamp'].max() - group['timestamp'].min()).total_seconds()
            if duration >= self.min_relax_sec:
                segments.append(group)
                
        return segments

    def fit_and_diagnose(self, segment_df):
        """
        Fits the relaxation model to the voltage data of a specific segment.
        Returns a dictionary containing fitted parameters and diagnostics.
        """
        # Time array must start at 0
        t_array = (segment_df['timestamp'] - segment_df['timestamp'].iloc[0]).dt.total_seconds().values
        v_array = segment_df['voltage'].values
        
        # Initial parameter guesses (P0)
        # ocv_t0 ~ first voltage point, a ~ 0.1V, tau_d ~ 500s, k_leak ~ 0
        p0 = [v_array[0], 0.1, 500.0, 0.0]
        
        # Physical bounds
        # ocv_t0: [v_min, v_max]
        # a: [0, 5.0] (polarization is always positive drop)
        # tau_d: [10, 10000] (physical diffusion limits)
        # k_leak: [-1e-4, 1e-4] (allow small negative for noise, but mostly look for positive leakage)
        bounds = (
            [0.0, 0.0, 10.0, -1e-4], 
            [1000.0, 5.0, 10000.0, 1e-4]
        )
        
        try:
            popt, pcov = curve_fit(self._relaxation_model, t_array, v_array, p0=p0, bounds=bounds)
            ocv_t0, a, tau_d, k_leak = popt
            
            # Diagnostic Logic
            has_isc = bool(k_leak > self.leakage_thresh)
            
            # Simple equivalent resistance estimation (R_eq = V / I_leak)
            # This requires converting dV/dt into dSOC/dt based on an OCV curve.
            # For this MVP, we provide a placeholder proportional logic.
            # If a typical cell loses 1mV/hour (2.7e-7 V/s) naturally, a 10uV/s drop is massive.
            estimated_req_ohm = -1 # Placeholder
            if has_isc:
                # Roughly mapping leakage rate to Ohms (Highly dependent on cell capacity)
                # Just an illustrative translation for the JSON report
                estimated_req_ohm = round(1.0 / (k_leak * 1000), 2)
            
            return {
                "success": True,
                "duration_sec": float(t_array[-1]),
                "params": {
                    "ocv_initial_v": round(ocv_t0, 4),
                    "polarization_a_v": round(a, 4),
                    "tau_d_s": round(tau_d, 1),
                    "k_leak_v_s": float(f"{k_leak:.8f}")
                },
                "diagnostics": {
                    "has_isc": has_isc,
                    "severity": "WARNING" if has_isc else "NORMAL",
                    "estimated_req_ohm": estimated_req_ohm,
                    "k_leak_threshold": self.leakage_thresh
                }
            }
        except Exception as e:
            logger.error(f"Curve fitting failed: {e}")
            return {"success": False, "error": str(e)}

    def process_file(self, df):
        """End-to-end processing of a dataframe"""
        logger.info(f"Scanning for relaxation segments > {self.min_relax_sec}s...")
        segments = self.extract_relaxation_segments(df)
        
        if not segments:
            logger.warning("No valid relaxation segments found. Diagnostics aborted.")
            return []
            
        logger.info(f"Found {len(segments)} valid relaxation segment(s). Running Non-Linear Fit...")
        
        results = []
        for i, seg in enumerate(segments):
            res = self.fit_and_diagnose(seg)
            res['segment_index'] = i
            res['start_time'] = str(seg['timestamp'].iloc[0])
            res['end_time'] = str(seg['timestamp'].iloc[-1])
            results.append(res)
            
        return results

def main():
    parser = argparse.ArgumentParser(description='Cloud P2D/SPM ISC Diagnostics')
    parser.add_argument('--input', required=True, help='Path to pre-processed features CSV')
    parser.add_argument('--output', required=True, help='Path to output JSON report')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        return

    logger.info(f"Reading input data from {args.input}")
    # Force parse timestamp
    df = pd.read_csv(args.input)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    analyzer = P2dIscDiagnostics(current_threshold=0.5, min_relax_seconds=1800)
    reports = analyzer.process_file(df)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(reports, f, indent=4, ensure_ascii=False)
        
    logger.info(f"Diagnostics complete. Report saved to {args.output}")

if __name__ == '__main__':
    main()
