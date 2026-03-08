import pandas as pd
import numpy as np
import subprocess
import os
import json

# Paths
DATA_DIR = r"d:\ASGARD\data\皇岗场站数据模拟\data\cluster1"
BASE_DIR = r"d:\ASGARD\BAS\L3-云端层级"
TEMP_DIR = os.path.join(BASE_DIR, "temp_test_data")
os.makedirs(TEMP_DIR, exist_ok=True)

def run_script(script_path, input_csv, output_json):
    cmd = f"python {script_path} --input {input_csv} --output {output_json}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=os.path.dirname(script_path))
    if result.returncode != 0:
        print(f"Error running {script_path}:\n{result.stderr}")
        return None
    with open(output_json, 'r') as f:
        return json.load(f)

def test_self_discharge_isc():
    print("\n--- Testing C3.2 P2D ISC (Self-Discharge) on Pack 05 ---")
    pack5_file = os.path.join(DATA_DIR, "pack_005_20251201.csv")
    df = pd.read_csv(pack5_file)
    
    # We test Cell 11 (High Self-Discharge) and Cell 01 (Normal)
    cells_to_test = {'Cell 11 (Abnormal)': 'CellVol11', 'Cell 01 (Normal)': 'CellVol1'}
    
    script_path = os.path.join(BASE_DIR, r"c3-2-isc-p2d\templates\python\p2d_isc_diagnosis.py")
    
    for label, col in cells_to_test.items():
        cell_df = df[['timestamp', col, 'Current', 'Temperature']].copy()
        cell_df.rename(columns={col: 'voltage', 'Current': 'current', 'Temperature': 'temperature'}, inplace=True)
        # Fix timestamp if needed
        cell_df['timestamp'] = pd.to_datetime(cell_df['timestamp'])
        
        temp_csv = os.path.join(TEMP_DIR, f"temp_pack5_{col}.csv")
        temp_json = os.path.join(TEMP_DIR, f"res_pack5_{col}.json")
        cell_df.to_csv(temp_csv, index=False)
        
        res = run_script(script_path, temp_csv, temp_json)
        if res:
            # Result could be a list of segment reports (C3.2 returns list)
            if isinstance(res, list):
                # find the one with highest leakage
                max_leak = max(res, key=lambda x: x['params']['k_leak_v_s']) if res else None
                if max_leak:
                    print(f"{label}: k_leak = {max_leak['params']['k_leak_v_s']:.7e} V/s | ISC Status: {max_leak['diagnostics']['severity']}")
                else:
                    print(f"{label}: No relaxation segments found.")
            else:
                 print(f"{label} Raw response: {res}")

def test_lithium_plating():
    print("\n--- Testing C3.13 Lithium Plating on Pack 08 ---")
    pack8_file = os.path.join(DATA_DIR, "pack_008_20251201.csv")
    df = pd.read_csv(pack8_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Extract post-charge relaxation. The charge ends at 04:00 and 13:00.
    # Let's take 04:00 to 05:00 as the relaxation window.
    mask = (df['timestamp'].dt.hour >= 4) & (df['timestamp'].dt.hour < 5)
    df_relax = df[mask].copy()
    
    cells_to_test = {'Cell 15 (Plating)': 'CellVol15', 'Cell 01 (Normal)': 'CellVol1'}
    script_path = os.path.join(BASE_DIR, r"c3-13-lithium-plating\templates\python\lithium_plating_relax.py")
    
    for label, col in cells_to_test.items():
        cell_df = df_relax[['timestamp', col]].copy()
        cell_df.rename(columns={col: 'voltage'}, inplace=True)
        
        temp_csv = os.path.join(TEMP_DIR, f"temp_pack8_{col}.csv")
        temp_json = os.path.join(TEMP_DIR, f"res_pack8_{col}.json")
        cell_df.to_csv(temp_csv, index=False)
        
        res = run_script(script_path, temp_csv, temp_json)
        if res:
            print(f"{label}: Status: {res.get('status')} | Plating Events Found: len={len(res.get('plating_events', []))}")

def test_safety_entropy():
    print("\n--- Testing C3.5 Safety Entropy (Consistency) on Pack 01 ---")
    # Pack 01 has Cell 07 with capacity fade, which should manifest as larger voltage deviation during deep discharge.
    pack1_file = os.path.join(DATA_DIR, "pack_001_20251201.csv")
    df = pd.read_csv(pack1_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Let's pick a snapshot at the end of the discharge cycle, e.g. 11:55:00 or somewhere SOC is low.
    snapshot_time = df['timestamp'].dt.strftime('%H:%M:%S') == '11:55:00'
    if not snapshot_time.any():
        print("Could not find exact time, taking row 43000 (roughly ~11:56)")
        snapshot = df.iloc[43000]
    else:
        snapshot = df[snapshot_time].iloc[0]
        
    # Construct the format for C3.5: cell_id, voltage, temperature
    cells = []
    volts = []
    temps = []
    for i in range(1, 21):
        cells.append(i)
        volts.append(snapshot[f'CellVol{i}'])
        temps.append(snapshot['Temperature']) # using pack temp as proxy
        
    pack_df = pd.DataFrame({'cell_id': cells, 'voltage': volts, 'temperature': temps})
    temp_csv = os.path.join(TEMP_DIR, "temp_pack1_snapshot.csv")
    temp_json = os.path.join(TEMP_DIR, "res_pack1_entropy.json")
    pack_df.to_csv(temp_csv, index=False)
    
    script_path = os.path.join(BASE_DIR, r"c3-5-safety-entropy\templates\python\safety_entropy.py")
    res = run_script(script_path, temp_csv, temp_json)
    if res:
        print(f"Pack 01 Snapshot Entropy result: Score {res.get('safety_score_0_100')}/100 | Status: {res.get('diagnostics',{}).get('status')}")

if __name__ == "__main__":
    print("Starting integration tests on ESS Mock Data...")
    test_self_discharge_isc()
    test_lithium_plating()
    test_safety_entropy()
