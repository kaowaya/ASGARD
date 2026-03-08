import pandas as pd
import numpy as np
import subprocess
import os
import json

BASE_DIR = r"d:\ASGARD\BAS\L3-云端层级"
DATA_DIR = r"d:\ASGARD\data\皇岗场站数据模拟\data\cluster1"
TEMP_DIR = os.path.join(BASE_DIR, "temp_metrics_data")
os.makedirs(TEMP_DIR, exist_ok=True)

def run_script(script_path, input_csv, output_json):
    cmd = f"python {script_path} --input {input_csv} --output {output_json}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=os.path.dirname(script_path))
    if result.returncode != 0:
        return None
    with open(output_json, 'r') as f:
        return json.load(f)

def calculate_metrics(y_true, y_pred, name="Algorithm"):
    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == True and yp == True)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == False and yp == True)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == True and yp == False)
    tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == False and yp == False)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    print(f"\n--- Metrics for {name} ---")
    print(f"Total Samples: {len(y_true)}")
    print(f"True Positives (TP): {tp} (Correctly caught anomalies)")
    print(f"False Positives (FP): {fp} (False alarms)")
    print(f"False Negatives (FN): {fn} (Missed anomalies)")
    print(f"True Negatives (TN): {tn} (Correctly ignored normal cells)")
    print(f"-> Precision (查准率): {precision*100:.2f}%")
    print(f"-> Recall (查全率): {recall*100:.2f}%")
    print(f"-> F1 Score: {f1*100:.2f}%")
    return precision, recall

def verify_lithium_plating():
    print("\n[Running] Verifying C3.13 Lithium Plating on Pack 08 (20 Cells)...")
    pack8_file = os.path.join(DATA_DIR, "pack_008_20251201.csv")
    df = pd.read_csv(pack8_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Extract relaxation window 04:00 to 05:00
    mask = (df['timestamp'].dt.hour >= 4) & (df['timestamp'].dt.hour < 5)
    df_relax = df[mask].copy()
    
    y_true = []
    y_pred = []
    
    script_path = os.path.join(BASE_DIR, r"c3-13-lithium-plating\templates\python\lithium_plating_relax.py")
    
    for i in range(1, 21):
        col = f'CellVol{i}'
        is_anomaly = True if i == 15 else False  # Ground truth from data_description.md
        
        cell_df = df_relax[['timestamp', col]].copy()
        cell_df.rename(columns={col: 'voltage'}, inplace=True)
        
        temp_csv = os.path.join(TEMP_DIR, f"temp_p8_c{i}.csv")
        temp_json = os.path.join(TEMP_DIR, f"res_p8_c{i}.json")
        cell_df.to_csv(temp_csv, index=False)
        
        res = run_script(script_path, temp_csv, temp_json)
        pred_anomaly = False
        if res and res.get('status') == 'DANGER':
            pred_anomaly = True
            
        y_true.append(is_anomaly)
        y_pred.append(pred_anomaly)

        if pred_anomaly and not is_anomaly:
            print(f"  [FP Warning] Cell {i} falsely flagged as Plating.")
        elif not pred_anomaly and is_anomaly:
            print(f"  [FN Warning] Cell {i} plating missed.")
            
    calculate_metrics(y_true, y_pred, "C3.13 Lithium Plating (Relaxation)")

def verify_isc_self_discharge():
    print("\n[Running] Verifying C3.2 ISC/Self-Discharge on Pack 05 (20 Cells)...")
    pack5_file = os.path.join(DATA_DIR, "pack_005_20251201.csv")
    df = pd.read_csv(pack5_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    y_true = []
    y_pred = []
    
    script_path = os.path.join(BASE_DIR, r"c3-2-isc-p2d\templates\python\p2d_isc_diagnosis.py")
    
    for i in range(1, 21):
        col = f'CellVol{i}'
        # Ground truth: Pack 05 Cell 11 and Cell 18
        is_anomaly = True if i in [11, 18] else False
        
        cell_df = df[['timestamp', col, 'Current', 'Temperature']].copy()
        cell_df.rename(columns={col: 'voltage', 'Current': 'current', 'Temperature': 'temperature'}, inplace=True)
        
        temp_csv = os.path.join(TEMP_DIR, f"temp_p5_c{i}.csv")
        temp_json = os.path.join(TEMP_DIR, f"res_p5_c{i}.json")
        cell_df.to_csv(temp_csv, index=False)
        
        res = run_script(script_path, temp_csv, temp_json)
        pred_anomaly = False
        if res and isinstance(res, list):
            # Check if any segment triggered WARNING
            for seg in res:
                if seg.get('diagnostics', {}).get('severity') == 'WARNING':
                    pred_anomaly = True
                    break
                    
        y_true.append(is_anomaly)
        y_pred.append(pred_anomaly)

        if pred_anomaly and not is_anomaly:
            print(f"  [FP Warning] Cell {i} falsely flagged as ISC Leakage.")
        elif not pred_anomaly and is_anomaly:
            print(f"  [FN Warning] Cell {i} ISC Leakage missed.")

    calculate_metrics(y_true, y_pred, "C3.2 ISC Diagnosis (P2D Leakage)")

if __name__ == "__main__":
    print("Initiating fleet-scan formal validation of algorithm metrics...\n")
    verify_lithium_plating()
    verify_isc_self_discharge()
