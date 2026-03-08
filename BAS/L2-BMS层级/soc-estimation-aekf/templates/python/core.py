# templates/python/core.py
"""
AEKF SOC估计器核心算法 (BMS板端简化版)
基于双极化等效电路模型，并在EKF基础上增加 Sage-Husa 自适应噪声估计。

Usage:
    python core.py --input data_samples/input/dynamic_drive.csv --output data_samples/output/soc_result.csv
"""

import argparse
import logging
from pathlib import Path
import os
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# --- OCV-SOC 插值函数 ---
def interpolation_discharge(v):
    x = np.array([2.5, 2.82, 3.118, 3.179, 3.20, 3.249, 3.28, 3.295, 3.38])
    y = np.array([0,   0.01, 0.08,  0.213, 0.284,0.67,  0.77, 0.995, 1.0])
    return np.interp(v, x, y)

def diff_v_to_soc(soc):
    # D(V)/D(SOC) 近似常数 0.4 
    return 0.4

def _v2soc_curve(soc):
    return 3.2 + 0.4 * soc

class AEKF_Estimator:
    def __init__(self, capacity_ah, dt=1.0, b=0.97):
        self.dt = dt
        self.Qn_As = capacity_ah * 3600.0
        self.b = b # Sage-Husa 遗忘因子
        
        # 简化模型参数 (LFP)
        self.R0 = 0.0003
        self.R1, self.C1 = 0.0001, 20000.0
        self.R2, self.C2 = 0.0004, 100000.0
        
        self.tau1 = self.R1 * self.C1
        self.tau2 = self.R2 * self.C2
        self.e1 = np.exp(-self.dt / self.tau1)
        self.e2 = np.exp(-self.dt / self.tau2)
        
        self.x = np.zeros((4, 1)) # [0: dummy, 1: U_p1, 2: U_p2, 3: SOC]^T
        self.P = np.eye(4) * 0.1
        
        self.Q = np.eye(4) * 1e-4
        self.R = np.array([[1e-2]])
        
        self.k = 0 # step count
        self.is_initialized = False

    def init_state(self, v_init):
        soc_init = interpolation_discharge(v_init)
        self.x[3, 0] = soc_init
        self.is_initialized = True
        logger.info(f"AEKF Initialized SOC based on V={v_init:.3f}V: {soc_init:.2%}")

    def step(self, ik, vk):
        if not self.is_initialized:
            self.init_state(vk)
            
        A = np.array([
            [0, 0, 0, 0],
            [0, self.e1, 0, 0],
            [0, 0, self.e2, 0],
            [0, 0, 0, 1]
        ])
        
        B = np.array([
            [0],
            [self.R1 * (1 - self.e1)],
            [self.R2 * (1 - self.e2)],
            [-self.dt / self.Qn_As]
        ])
        
        u = np.array([[ik]])
        
        # 1. 预测
        x_pre = A @ self.x + B @ u
        P_pre = A @ self.P @ A.T + self.Q
        y_pre = _v2soc_curve(x_pre[3, 0]) - x_pre[1, 0] - x_pre[2, 0] - ik * self.R0
        
        H = np.array([[-1, -1, -1, diff_v_to_soc(x_pre[3, 0])]])
        
        # 新息 (Innovation)
        epsilon = vk - y_pre
        
        # --- Sage-Husa 自适应更新 ---
        # 遗忘递推系数
        d_k = (1.0 - self.b) / (1.0 - self.b**(self.k + 1))
        
        # 更新观测噪声方差 R
        R_new = (1 - d_k) * self.R + d_k * (epsilon**2)
        self.R = np.clip(R_new, 1e-4, 1.0) # 工业发散限制
        # -----------------------------
        
        # 2. 测量更新
        S = H @ P_pre @ H.T + self.R
        K = P_pre @ H.T @ np.linalg.inv(S)
        
        self.x = x_pre + K * epsilon
        self.P = P_pre - K @ H @ P_pre
        
        # --- 更新过程噪声协方差 Q ---
        Q_new = (1 - d_k) * self.Q + d_k * (K @ np.array([[epsilon**2]]) @ K.T)
        self.Q = np.clip(Q_new, 1e-6, 0.1)
        # -----------------------------
        
        self.x[3, 0] = np.clip(self.x[3, 0], 0.0, 1.0)
        self.k += 1
        
        return self.x[3, 0], y_pre, float(self.R[0][0])

def run_aekf(input_file, capacity):
    df = pd.read_csv(input_file)
    logger.info(f"Data length: {len(df)}")
    estimator = AEKF_Estimator(capacity_ah=capacity)
    
    results = []
    for idx, row in df.iterrows():
        ik = row['current']
        vk = row['voltage']
        
        soc, v_est, r_obs = estimator.step(ik, vk)
        results.append({
            'timestamp': row.get('timestamp', idx),
            'current': ik,
            'voltage': vk,
            'SOC': soc,
            'V_est': v_est,
            'R_obs': r_obs
        })
    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description='AEKF SOC Estimator')
    parser.add_argument('--input', required=True, help='输入CSV文件')
    parser.add_argument('--output', required=True, help='输出CSV文件')
    parser.add_argument('--capacity', type=float, default=235.0, help='电池容量(Ah)')
    args = parser.parse_args()

    logger.info(f"🚀 启动 AEKF SOC估计")
    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        return
        
    res_df = run_aekf(args.input, args.capacity)
    
    out_dir = Path(args.output).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    res_df.to_csv(args.output, index=False)
    logger.info(f"✓ 结果已保存: {args.output}")
    logger.info(f"📊 最终SOC: {res_df['SOC'].iloc[-1]:.2%}")

if __name__ == '__main__':
    main()
