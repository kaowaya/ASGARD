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

def test_entropy_on_pack(pack_num, target_time='11:55:00'):
    pack_name = f"pack_{pack_num:03d}"
    print(f"\n--- Testing C3.5 Safety Entropy on {pack_name} ---")
    pack_file = os.path.join(DATA_DIR, f"{pack_name}_20251201.csv")
    df = pd.read_csv(pack_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Get snapshot
    snapshot_time = df['timestamp'].dt.strftime('%H:%M:%S') == target_time
    if not snapshot_time.any():
        print(f"Time {target_time} not found. Taking row 43000")
        snapshot = df.iloc[43000]
    else:
        snapshot = df[snapshot_time].iloc[0]
        
    cells = []
    volts = []
    temps = []
    for i in range(1, 21):
        cells.append(i)
        volts.append(snapshot[f'CellVol{i}'])
        temps.append(snapshot['Temperature'])
        
    pack_df = pd.DataFrame({'cell_id': cells, 'voltage': volts, 'temperature': temps})
    temp_csv = os.path.join(TEMP_DIR, f"temp_{pack_name}_snapshot.csv")
    temp_json = os.path.join(TEMP_DIR, f"res_{pack_name}_entropy.json")
    pack_df.to_csv(temp_csv, index=False)
    
    script_path = os.path.join(BASE_DIR, r"c3-5-safety-entropy\templates\python\safety_entropy.py")
    res = run_script(script_path, temp_csv, temp_json)
    
    if res:
        print(f"{pack_name} Result: Score {res.get('safety_score_0_100')}/100 | Status: {res.get('diagnostics',{}).get('status')} | Entropy: {res.get('joint_entropy', 0):.4f}")
        print("Voltages:")
        print(pack_df['voltage'].describe())

if __name__ == "__main__":
    test_entropy_on_pack(1, '11:55:00') # Pack 1 (SOH 94.5%)
    test_entropy_on_pack(3, '11:55:00') # Pack 3 (SOH 93.8% - Worse)
    test_entropy_on_pack(2, '11:55:00') # Pack 2 (SOH 95.2%)
    test_entropy_on_pack(9, '11:55:00') # Pack 9 (All cells normal ~98%)
