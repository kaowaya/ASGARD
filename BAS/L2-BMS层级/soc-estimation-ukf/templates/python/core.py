# templates/python/core.py
"""
UKF SOC估计器核心算法 (BMS板端简化版)
基于无迹变换 (Unscented Transform)，针对强非线性电池进行状态估计。

Usage:
    python core.py --input data_samples/input/nonlinear_test.csv --output data_samples/output/soc_result.csv
"""

import argparse
import logging
from pathlib import Path
import os
import pandas as pd
import numpy as np
import scipy.linalg

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# --- 模拟极其非线性的 OCV-SOC 平台区函数 ---
def nonlinear_ocv(soc):
    # LFP 特征：两头翘，中间极平
    v_base = 3.2
    if soc < 0.1:
        return 2.5 + (v_base - 2.5) * (soc / 0.1)
    elif soc > 0.9:
        return v_base + (3.6 - v_base) * ((soc - 0.9) / 0.1)
    else:
        # 中间的微小非线性波动
        return v_base + 0.1 * (soc - 0.5) + 0.02 * np.sin(soc * 10 * np.pi)

def interpolation_soc(v):
    # 为初始化写的粗略反查表
    x = np.array([2.5, 3.1, 3.2, 3.25, 3.3, 3.6])
    y = np.array([0,   0.09,0.5, 0.8,  0.9, 1.0])
    return np.interp(v, x, y)


class UKF_Estimator:
    def __init__(self, capacity_ah, dt=1.0):
        self.dt = dt
        self.Qn_As = capacity_ah * 3600.0
        
        # 简化模型参数
        self.R0 = 0.0003
        self.R1, self.C1 = 0.0001, 20000.0
        self.R2, self.C2 = 0.0004, 100000.0
        
        self.tau1 = self.R1 * self.C1
        self.tau2 = self.R2 * self.C2
        self.e1 = np.exp(-self.dt / self.tau1)
        self.e2 = np.exp(-self.dt / self.tau2)
        
        # N=3 维状态变量: [U_p1, U_p2, SOC]^T
        self.N = 3
        self.x = np.zeros(self.N)
        self.P = np.eye(self.N) * 0.01
        
        self.Q = np.eye(self.N) * 1e-5
        self.R = np.array([[1e-3]]) # 观测噪声
        
        # UT 参数
        self.alpha = 1e-3
        self.beta = 2.0
        self.kappa = 0.0
        
        self.lambda_ = self.alpha**2 * (self.N + self.kappa) - self.N
        self.gamma = np.sqrt(self.N + self.lambda_)
        
        # 预计算权重
        self.Wm = np.zeros(2 * self.N + 1)
        self.Wc = np.zeros(2 * self.N + 1)
        self.Wm[0] = self.lambda_ / (self.N + self.lambda_)
        self.Wc[0] = self.Wm[0] + (1 - self.alpha**2 + self.beta)
        for i in range(1, 2 * self.N + 1):
            self.Wm[i] = 1.0 / (2 * (self.N + self.lambda_))
            self.Wc[i] = 1.0 / (2 * (self.N + self.lambda_))
            
        self.is_initialized = False

    def init_state(self, v_init):
        soc_init = interpolation_soc(v_init)
        self.x[2] = soc_init
        self.is_initialized = True
        logger.info(f"UKF Initialized SOC: {soc_init:.2%}")

    def f_state_transition(self, x_pts, current_ik):
        """非线性状态转移函数"""
        pt_out = np.zeros_like(x_pts)
        pt_out[0] = x_pts[0] * self.e1 + self.R1 * (1 - self.e1) * current_ik
        pt_out[1] = x_pts[1] * self.e2 + self.R2 * (1 - self.e2) * current_ik
        pt_out[2] = x_pts[2] - (current_ik * self.dt) / self.Qn_As
        # 物理截断防御
        pt_out[2] = np.clip(pt_out[2], 0.0, 1.0)
        return pt_out

    def h_observation(self, x_pts, current_ik):
        """非线性观测函数"""
        soc = x_pts[2]
        up1, up2 = x_pts[0], x_pts[1]
        v_pred = nonlinear_ocv(soc) - up1 - up2 - current_ik * self.R0
        return np.array([v_pred])

    def step(self, ik, vk):
        if not self.is_initialized:
            self.init_state(vk)
            
        # 1. 生成 Sigma 点 (Cholesky 分解带鲁棒保护)
        try:
            # 加上一个极小对角防崩溃
            P_safe = self.P + np.eye(self.N)*1e-8
            L = scipy.linalg.cholesky(P_safe, lower=True)
        except scipy.linalg.LinAlgError:
            logger.warning("P Matrix non-positive! Resetting diagonal.")
            P_diag = np.diag(np.diag(self.P))
            P_diag[P_diag <= 0] = 1e-4
            L = scipy.linalg.cholesky(P_diag, lower=True)
            self.P = P_diag

        X_sigma = np.zeros((2 * self.N + 1, self.N))
        X_sigma[0] = self.x
        for i in range(self.N):
            X_sigma[i + 1] = self.x + self.gamma * L[:, i]
            X_sigma[self.N + i + 1] = self.x - self.gamma * L[:, i]
            
        # 2. 时间更新 (预测)
        X_sigma_pred = np.zeros_like(X_sigma)
        for i in range(2 * self.N + 1):
            X_sigma_pred[i] = self.f_state_transition(X_sigma[i], ik)
            
        # 加权重构先验状态
        x_pre = np.zeros(self.N)
        for i in range(2 * self.N + 1):
            x_pre += self.Wm[i] * X_sigma_pred[i]
            
        # 先验协方差
        P_pre = np.copy(self.Q)
        for i in range(2 * self.N + 1):
            diff = X_sigma_pred[i] - x_pre
            P_pre += self.Wc[i] * np.outer(diff, diff)
            
        # 为了计算协方差Py, 我们需要重新在这个先验附近采Sigma点 (或者复用)
        # 工业上为了省算力常直接复用传播后的点
        Y_sigma_pred = np.zeros((2 * self.N + 1, 1))
        for i in range(2 * self.N + 1):
            Y_sigma_pred[i] = self.h_observation(X_sigma_pred[i], ik)
            
        y_pre = np.zeros(1)
        for i in range(2 * self.N + 1):
            y_pre += self.Wm[i] * Y_sigma_pred[i]
            
        # 3. 测量更新
        Py = np.copy(self.R)
        Pxy = np.zeros((self.N, 1))
        
        for i in range(2 * self.N + 1):
            ydiff = Y_sigma_pred[i] - y_pre
            xdiff = X_sigma_pred[i] - x_pre
            Py += self.Wc[i] * np.outer(ydiff, ydiff)
            Pxy += self.Wc[i] * np.outer(xdiff, ydiff)
            
        K = Pxy @ np.linalg.inv(Py)
        
        # 状态校正
        self.x = x_pre + (K @ (np.array([vk]) - y_pre)).flatten()
        self.P = P_pre - K @ Py @ K.T
        
        self.x[2] = np.clip(self.x[2], 0.0, 1.0)
        
        return self.x[2], float(y_pre[0])

def run_ukf(input_file, capacity):
    df = pd.read_csv(input_file)
    estimator = UKF_Estimator(capacity_ah=capacity)
    
    results = []
    for idx, row in df.iterrows():
        ik = row['current']
        vk = row['voltage']
        
        soc, v_est = estimator.step(ik, vk)
        results.append({
            'timestamp': row.get('timestamp', idx),
            'current': ik,
            'voltage': vk,
            'SOC': soc,
            'V_est': v_est
        })
    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description='UKF SOC Estimator')
    parser.add_argument('--input', required=True, help='输入CSV文件')
    parser.add_argument('--output', required=True, help='输出CSV文件')
    parser.add_argument('--capacity', type=float, default=235.0, help='电池容量(Ah)')
    args = parser.parse_args()

    logger.info(f"🚀 启动 UKF SOC估计核心验证板")
    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        return
        
    res_df = run_ukf(args.input, args.capacity)
    
    out_dir = Path(args.output).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    res_df.to_csv(args.output, index=False)
    logger.info(f"✓ 结果已保存: {args.output}")
    logger.info(f"📊 最终SOC: {res_df['SOC'].iloc[-1]:.2%}")

if __name__ == '__main__':
    main()
