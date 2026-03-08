# templates/python/core.py
"""
EKF SOC估计器核心算法 (BMS板端简化版)
基于双极化等效电路模型，参数固定

Usage:
    python core.py --input data.csv --output result.csv --battery lfp_default
"""

import argparse
import logging
from pathlib import Path
import os
import pandas as pd
import numpy as np

# 配置日志
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# --- OCV-SOC 插值函数 (内置默认版，实际从配置读最佳) ---
def interpolation_discharge(v):
    x = np.array([2.5, 2.5, 2.82, 2.937, 3.09, 3.118, 3.142, 3.16, 3.179, 3.20, 3.234, 3.249, 3.28, 3.289, 3.295, 3.38])
    y = np.array([0, 0.002, 0.01, 0.035, 0.065, 0.08, 0.09, 0.18, 0.213, 0.284, 0.41, 0.67, 0.77, 0.99, 0.995, 1])
    return np.interp(v, x, y)

def interpolation_charge(v):
    x = np.array([2.6, 2.70, 3.1, 3.19, 3.246, 3.256, 3.29, 3.325, 3.331, 3.345, 3.37, 3.385, 3.4, 3.45, 3.5])
    y = np.array([0, 0.002, 0.05, 0.06, 0.088, 0.144, 0.21, 0.30, 0.33, 0.65, 0.73, 0.95, 0.96, 0.988, 1])
    return np.interp(v, x, y)

def v_to_soc(v, is_charge=False):
    """基于电压初始化SOC"""
    if v < 2.5: return 0.0
    if v > 3.5: return 1.0
    if is_charge:
        return interpolation_charge(v) + 0.16
    else:
        return interpolation_discharge(v) + 0.16

def diff_v_to_soc(soc):
    """ d(V)/d(SOC) """
    # 简化为多项式求导，此处使用 C 代码中相同系数
    coef = np.array([-2.89046252, 270.21418, -4136.87949, 28608.0318,
                    -110034.214, 254597.836, -362585.024, 311126.95,
                    -147564.814, 29721.193])
    soc_pows = np.array([soc**i for i in range(10)])
    return np.sum(coef * soc_pows)

def _v2soc_curve(soc):
    coef = np.array([2.89, -2.89046252, 135.10709, -1378.95983,
                    7152.00796, -22006.8427, 42432.9727, -51797.8605,
                    38890.8687, -16396.0905, 2972.1193])
    soc_pows = np.array([soc**i for i in range(11)])
    return np.sum(coef * soc_pows)

def load_battery_params(battery_name):
    """模拟加载参数，实际应解析YAML"""
    if 'lfp' in battery_name.lower():
        return {
            'Qn': 235.0, # Ah
            'R0': 0.000328,
            'R1': 0.00007224,
            'R2': 0.0004735,
            'C1': 22960.92,
            'C2': 101484.95,
            'dt': 1.0
        }
    else:
        raise ValueError(f"Unknown battery type: {battery_name}")

class EKF_Estimator:
    def __init__(self, params):
        self.dt = params['dt']
        self.Qn_As = params['Qn'] * 3600.0
        
        # 模型参数
        self.R0 = params['R0']
        self.R1 = params['R1']
        self.R2 = params['R2']
        self.C1 = params['C1']
        self.C2 = params['C2']
        
        self.tau1 = self.R1 * self.C1
        self.tau2 = self.R2 * self.C2
        self.e1 = np.exp(-self.dt / self.tau1)
        self.e2 = np.exp(-self.dt / self.tau2)
        
        # 状态: x = [0: dummy, 1: U_p1, 2: U_p2, 3: SOC]^T
        self.x = np.zeros((4, 1))
        # 协方差
        self.P = np.eye(4)
        
        # 噪声参数 Q, R
        self.Q = np.eye(4) * 0.01
        self.R = np.eye(1) * 0.01
        
        self.is_initialized = False

    def init_state(self, v_init, i_init):
        # 基于第一点电压和电流计算初始SOC
        is_charge = i_init < 0
        soc_init = v_to_soc(v_init, is_charge=is_charge)
        
        self.x[3, 0] = soc_init
        self.is_initialized = True
        logger.info(f"Initialized SOC based on V={v_init:.3f}V: {soc_init:.2%}")

    def step(self, ik, vk):
        if not self.is_initialized:
            self.init_state(vk, ik)
            
        A = np.array([
            [0, 0, 0, 0],
            [0, self.e1, 0, 0],
            [0, 0, self.e2, 0],
            [0, 0, 0, 1]
        ])
        
        B = np.array([
            [self.R0],
            [self.R1 * (1 - self.e1)],
            [self.R2 * (1 - self.e2)],
            [-self.dt / self.Qn_As] # 此处电流充电为负，积分符号看具体约定
        ])
        
        # 1. 预测 (Time Update)
        u = np.array([[ik]])
        x_pre = A @ self.x + B @ u
        P_pre = A @ self.P @ A.T + self.Q
        
        # 模型预测电压
        y_pre = _v2soc_curve(x_pre[3, 0]) - x_pre[1, 0] - x_pre[2, 0] - ik * self.R0
        
        # 2. 测量更新 (Measurement Update)
        # H = d(y)/dx
        H = np.array([[-1, -1, -1, diff_v_to_soc(x_pre[3, 0])]])
        
        # 新息协方差
        S = H @ P_pre @ H.T + self.R
        
        # 卡尔曼增益
        K = P_pre @ H.T @ np.linalg.inv(S)
        
        # 状态更新
        v_err = vk - y_pre
        self.x = x_pre + K * v_err
        
        # 协方差更新
        self.P = P_pre - K @ H @ P_pre
        
        # 防溢出保护
        self.x[3, 0] = np.clip(self.x[3, 0], 0.0, 1.0)
        
        return self.x[3, 0], self.x[1, 0], self.x[2, 0], y_pre

def run_ekf(input_file, params):
    df = pd.read_csv(input_file)
    logger.info(f"Data length: {len(df)}")
    
    estimator = EKF_Estimator(params)
    
    results = []
    
    for idx, row in df.iterrows():
        # 这里假设列名匹配，根据需要修改
        # 如果数据列名为大写或不同名，请做预处理映射
        ik = row['current']
        vk = row['voltage']
        
        soc, up1, up2, v_est = estimator.step(ik, vk)
        
        results.append({
            'timestamp': row.get('timestamp', idx),
            'SOC': soc,
            'V_est': v_est
        })
        
    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description='EKF SOC Estimator')
    parser.add_argument('--input', required=True, help='输入CSV文件')
    parser.add_argument('--output', required=True, help='输出CSV文件')
    parser.add_argument('--battery', default='lfp_default', help='电池参数文件名')
    args = parser.parse_args()

    logger.info(f"🚀 启动 EKF SOC估计")
    params = load_battery_params(args.battery)
    
    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        return
        
    res_df = run_ekf(args.input, params)
    
    # ensure output dir exists
    out_dir = Path(args.output).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    
    res_df.to_csv(args.output, index=False)
    logger.info(f"✓ 结果已保存: {args.output}")
    logger.info(f"📊 最终SOC: {res_df['SOC'].iloc[-1]:.2%}")

if __name__ == '__main__':
    main()
