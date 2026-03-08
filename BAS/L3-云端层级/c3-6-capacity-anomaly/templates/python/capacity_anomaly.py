# templates/python/capacity_anomaly.py
"""
ASGARD C3.6 Cloud Capacity Anomaly Detection (Isolation Forest)

Performs unsupervised anomaly detection on a fleet of batteries to identify
units that are degrading significantly faster than their peers under similar
usage conditions.

Usage:
    python capacity_anomaly.py --input fleet_stats.csv --output anomalies.json
"""

import argparse
import pandas as pd
import numpy as np
import json
import os
import logging
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def detect_fleet_anomalies(df, contamination=0.05):
    """
    Runs Isolation Forest on fleet data.
    Expected columns: ['battery_id', 'dod_avg', 'fast_charge_ratio', 'temp_avg', 'current_capacity_ah']
    """
    features = ['dod_avg', 'fast_charge_ratio', 'temp_avg', 'current_capacity_ah']
    
    # Check if all required features exist
    for f in features:
        if f not in df.columns:
            logger.error(f"Missing required feature column: {f}")
            return {"success": False, "error": f"Missing column {f}"}
            
    X = df[features].fillna(df[features].median()) # Basic median imputation for safety
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Initialize and fit Isolation Forest
    # contamination defines the proportion of outliers in the data set
    clf = IsolationForest(n_estimators=100, max_samples='auto', contamination=contamination, random_state=42)
    
    clf.fit(X_scaled)
    
    # Predict (-1 for outliers, 1 for inliers)
    preds = clf.predict(X_scaled)
    scores = clf.decision_function(X_scaled) # Lower is more anomalous
    
    df['anomaly_label'] = preds
    df['anomaly_score'] = scores
    
    # Filter anomalies
    anomalies_df = df[df['anomaly_label'] == -1].sort_values(by='anomaly_score')
    
    results = {
        "success": True,
        "total_analyzed": len(df),
        "total_anomalies_found": len(anomalies_df),
        "anomalous_batteries": []
    }
    
    for _, row in anomalies_df.iterrows():
        results["anomalous_batteries"].append({
            "battery_id": str(row['battery_id']),
            "score": round(row['anomaly_score'], 4),
            "current_capacity_ah": round(row['current_capacity_ah'], 2)
        })
        
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--contamination', type=float, default=0.05, help="Expected outlier ratio")
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        logger.warning("Input missing. Generating a 500-vehicle mock fleet data...")
        os.makedirs(os.path.dirname(args.input), exist_ok=True)
        # 490 normal vehicles
        ids = [f"VIN_{i:04d}" for i in range(500)]
        dod = np.random.normal(50.0, 10.0, 500)
        fc = np.random.normal(0.2, 0.1, 500)
        temp = np.random.normal(25.0, 2.0, 500)
        # Normal capacity around 100Ah
        cap = np.random.normal(98.0, 2.0, 500)
        
        # Inject 10 severe anomalies (low capacity despite normal usage, or extreme usage)
        for i in range(10):
            cap[i] = np.random.normal(75.0, 5.0) # Dropped capacity
            
        mock_df = pd.DataFrame({
            'battery_id': ids,
            'dod_avg': dod,
            'fast_charge_ratio': np.clip(fc, 0, 1),
            'temp_avg': temp,
            'current_capacity_ah': cap
        })
        mock_df.to_csv(args.input, index=False)

    df = pd.read_csv(args.input)
    res = detect_fleet_anomalies(df, args.contamination)
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(res, f, indent=4)
        
    logger.info(f"C3.6 Anomaly Detection completed. Found {res.get('total_anomalies_found')} anomalous units.")

if __name__ == '__main__':
    main()
