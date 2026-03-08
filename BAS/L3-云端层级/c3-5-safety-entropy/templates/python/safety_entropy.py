# templates/python/safety_entropy.py
"""
ASGARD C3.5 Cloud Safety Entropy Diagnostics

Calculates Shannon Entropy based on the distribution of delta V and delta T 
across all cells in a pack. Evaluates a normalized Safety Score from 0 to 100.

Usage:
    python safety_entropy.py --input pack_cells.csv --output score_report.json
"""

import argparse
import pandas as pd
import numpy as np
import json
import logging
import os

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def calculate_shannon_entropy(data, bins=20):
    """
    Helper function to calculate entropy of a 1D dataset.
    """
    hist, _ = np.histogram(data, bins=bins, density=True)
    # Convert density back to probability of falling in the bin
    # probability = density * bin_width. Since sum(probabilities) must = 1.
    p = hist / np.sum(hist)
    # Remove zeros for log calculation
    p = p[p > 0]
    
    entropy = -np.sum(p * np.log2(p))
    return entropy

def compute_pack_safety_score(df):
    """
    Calculates safety entropy from cross-sectional cell data.
    Assumes df has columns: ['cell_id', 'voltage', 'temperature'] for at least one snapshot.
    Normally, we run this on a time-window of dV/dt or dT/dt, but for static 
    anomalies (like one cell drooping), raw Delta works.
    """
    # 1. Voltage Entropy
    v_entropy = calculate_shannon_entropy(df['voltage'])
    
    # 2. Temperature Entropy
    t_entropy = calculate_shannon_entropy(df['temperature'])
    
    # 3. Create a pseudo-combined entropy risk factor
    # Base entropy for a perfectly matched pack might be around 0.5 ~ 1.0 depending on noise.
    # An aging pack might be 2.0. Severe short circuit might blow it up to 3.0+.
    total_entropy = v_entropy + t_entropy
    
    # Normalizing to a 0-100 Safety Score
    # Score 100 = 0 Entropy. Score 0 = Entropy >= 5.0
    safe_score = max(0.0, min(100.0, 100.0 - (total_entropy * 20.0)))
    
    return {
        "success": True,
        "metrics": {
            "voltage_entropy": round(v_entropy, 4),
            "temperature_entropy": round(t_entropy, 4),
            "total_entropy": round(total_entropy, 4)
        },
        "safety_score_0_100": int(safe_score),
        "diagnostics": {
            "status": "CRITICAL" if safe_score < 40 else ("WARNING" if safe_score < 70 else "HEALTHY")
        }
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        logger.warning("Input missing. Generating a 100-cell mock snapshot...")
        os.makedirs(os.path.dirname(args.input), exist_ok=True)
        # 99 Normal cells
        cells = list(range(100))
        v = np.random.normal(3.8, 0.005, 99).tolist()
        t = np.random.normal(30.0, 0.5, 99).tolist()
        # 1 Bad cell (voltage droop, hot)
        v.append(3.6)
        t.append(45.0)
        
        pd.DataFrame({'cell_id': cells, 'voltage': v, 'temperature': t}).to_csv(args.input, index=False)

    df = pd.read_csv(args.input)
    res = compute_pack_safety_score(df)
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(res, f, indent=4)
        
    logger.info(f"C3.5 Safety Entropy completed. Score: {res.get('safety_score_0_100')}/100")

if __name__ == '__main__':
    main()
