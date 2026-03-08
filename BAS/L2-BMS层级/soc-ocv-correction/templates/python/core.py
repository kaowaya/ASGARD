# templates/python/core.py
"""
OCV查表修正法SOC Estimator (BMS板端简化还原版)

Usage:
    python core.py --input data_samples/input/driving_with_rest.csv --output data_samples/output/soc_result.csv --capacity 235.0
"""

import argparse
import logging
import pandas as pd
from pathlib import Path
import os
import numpy as np

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# 极简OCV基准表（放电态）
OCV_X_LFP = np.array([2.50, 3.10, 3.20, 3.25, 3.28, 3.29, 3.30, 3.32, 3.35, 3.40, 3.50])
OCV_Y_LFP = np.array([0.00, 0.05, 0.10, 0.20, 0.40, 0.50, 0.60, 0.80, 0.90, 0.98, 1.00])

def lookup_soc_by_ocv(ocv):
    return np.interp(ocv, OCV_X_LFP, OCV_Y_LFP)

class OcvCorrectionSOC:
    def __init__(self, capacity_ah, rest_threshold_hours=2.0, max_jump_step=0.005):
        self.capacity_ah = capacity_ah
        self.rest_threshold_s = rest_threshold_hours * 3600
        self.max_jump_step = max_jump_step
        
        self.soc_real = 0.5
        self.soc_disp = 0.5
        self.last_time = None
        self.rest_timer_s = 0.0
        self.current_deadband = 0.05
        
        self.is_initialized = False

    def update(self, current_a, voltage_v, temp_c, timestamp_s):
        if not self.is_initialized:
            self.last_time = timestamp_s
            # 冷启动绝对信任首个电压点
            self.soc_real = lookup_soc_by_ocv(voltage_v)
            self.soc_disp = self.soc_real
            self.is_initialized = True
            return self.soc_real, self.soc_disp, False

        dt_s = timestamp_s - self.last_time
        self.last_time = timestamp_s
        if dt_s <= 0 or dt_s > 3600:
            return self.soc_real, self.soc_disp, False

        # 1. 静置计时 & 零漂过滤
        if abs(current_a) < self.current_deadband:
            current_a = 0.0
            self.rest_timer_s += dt_s
        else:
            self.rest_timer_s = 0.0

        # 2. 安时积分 (核心背景任务)
        eta = 1.0 if current_a <= 0 else 0.99
        dt_h = dt_s / 3600.0
        # 放电(正电流)减碳，充电(负电流)加碳
        d_soc = -(eta * current_a * dt_h) / self.capacity_ah
        
        self.soc_real += d_soc
        self.soc_real = max(0.0, min(1.0, self.soc_real))

        is_corrected = False
        # 3. 查表修正判定
        if self.rest_timer_s > self.rest_threshold_s:
            mapped_soc = lookup_soc_by_ocv(voltage_v)
            # 只有偏离 > 1% 才修正
            if abs(self.soc_real - mapped_soc) > 0.01:
                self.soc_real = mapped_soc
                is_corrected = True
                logger.info(f"✨ 触发OCV修正: V={voltage_v:.3f}V, Soc突变至 {self.soc_real:.2%}")

        # 4. 显示层防跳变融合 (工业级必备)
        soc_diff = self.soc_real - self.soc_disp
        step = 0.0
        if soc_diff > 0.0:
            step = min(self.max_jump_step, soc_diff)
            if current_a > 0: step = 0.0 # 放电中禁止电量数字抬头
            self.soc_disp += step
        elif soc_diff < 0.0:
            step = min(self.max_jump_step, -soc_diff)
            if current_a < 0: step = 0.0 # 充电中禁止电量数字倒扣
            self.soc_disp -= step

        self.soc_disp += (d_soc if current_a != 0.0 else 0)
        self.soc_disp = max(0.0, min(1.0, self.soc_disp))

        return self.soc_real, self.soc_disp, is_corrected

def run_estimators(input_file, capacity):
    df = pd.read_csv(input_file)
    # 模拟静置阈值为极其短暂的测试值 (10s)
    estimator = OcvCorrectionSOC(capacity_ah=capacity, rest_threshold_hours=10/3600.0, max_jump_step=0.01)
    
    results = []
    
    for idx, row in df.iterrows():
        tk = row['timestamp_s'] if 'timestamp_s' in row else idx
        ik = row['current']
        vk = row['voltage']
        temp = row['temperature'] if 'temperature' in row else 25.0
        
        soc_r, soc_d, corr = estimator.update(ik, vk, temp, tk)
        results.append({
            'timestamp_s': tk,
            'current': ik,
            'voltage': vk,
            'SOC_real': soc_r,
            'SOC_disp': soc_d,
            'is_corrected': 1 if corr else 0
        })
        
    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description='OCV Correction Estimator')
    parser.add_argument('--input', required=True, help='输入CSV文件')
    parser.add_argument('--output', required=True, help='输出CSV文件')
    parser.add_argument('--capacity', type=float, default=235.0, help='电池额定容量')
    args = parser.parse_args()

    logger.info(f"🚀 启动 OCV查表修正 SOC估计")
    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        return
        
    res_df = run_estimators(args.input, args.capacity)
    
    out_dir = Path(args.output).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    res_df.to_csv(args.output, index=False)
    logger.info(f"✓ 结果已保存: {args.output}")
    logger.info(f"📊 最终显示SOC: {res_df['SOC_disp'].iloc[-1]:.2%}")

if __name__ == '__main__':
    main()
