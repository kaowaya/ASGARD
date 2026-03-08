# templates/python/core.py
"""
安时积分算法 (Coulomb Counting SOC Estimator)核心实现 (BMS板端简化还原版)

Usage:
    python core.py --input data_samples/input/discharge_cycle.csv --output data_samples/output/soc_result.csv --capacity 235.0 --init-soc 1.0
"""

import argparse
import logging
import pandas as pd
from pathlib import Path
import os

# 配置日志
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class CoulombCountingSOC:
    def __init__(self, capacity_ah, initial_soc=0.5, current_deadband=0.05):
        self.Cn = capacity_ah     # 额定容量 Ah
        self.soc = initial_soc    # 初始SOC 0.0~1.0
        self.last_time = None
        self.deadband = current_deadband

    def calc_coulombic_efficiency(self, current_a, temp_c):
        """简化库伦效率计算"""
        # 约定：充电为负(吸收电流)，放电为正(输出电流)
        if current_a <= 0:  
            return 1.0
        else:
            t_ref = 25.0
            alpha = 0.005
            eta = 0.99 * (1.0 - alpha * (1.0 - temp_c / t_ref))
            return max(0.8, min(1.0, eta))

    def update(self, current_a, temp_c, timestamp_s):
        """单步SOC更新算法"""
        if self.last_time is None:
            self.last_time = timestamp_s
            return self.soc
            
        # 1. 过滤底噪死区
        if abs(current_a) < self.deadband:
            current_a = 0.0

        # 2. 计算时间增量转为小时
        dt_seconds = timestamp_s - self.last_time
        self.last_time = timestamp_s
        
        # 异常时间过滤(例如重启或者数据抖动)
        if dt_seconds <= 0 or dt_seconds > 3600:
            return self.soc
            
        dt_h = dt_seconds / 3600.0

        # 3. 计算库伦效率
        eta = self.calc_coulombic_efficiency(current_a, temp_c)

        # 4. 安时积分更新 (注意：充电电流为负，积分项减负即为加SOC；放电电流为正，积分项减正即为减SOC)
        d_soc = -(eta * current_a * dt_h) / self.Cn
        self.soc += d_soc

        # 5. 严格边界钳位保护 (Industrial-grade clamping)
        self.soc = max(0.0, min(1.0, self.soc))
        return self.soc

def run_estimators(input_file, capacity, init_soc):
    df = pd.read_csv(input_file)
    logger.info(f"Loaded {len(df)} rows from {input_file}")
    
    estimator = CoulombCountingSOC(capacity_ah=capacity, initial_soc=init_soc)
    
    results = []
    
    for idx, row in df.iterrows():
        # 这里假设列名匹配：时间秒、电流A、温度C
        tk = row['timestamp_s'] if 'timestamp_s' in row else idx # 若无时间戳，假定dt=1秒
        ik = row['current']
        temp = row['temperature'] if 'temperature' in row else 25.0
        
        soc = estimator.update(ik, temp, tk)
        
        results.append({
            'timestamp_s': tk,
            'current': ik,
            'SOC': soc
        })
        
    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description='Coulomb Counting SOC Estimator')
    parser.add_argument('--input', required=True, help='输入CSV文件')
    parser.add_argument('--output', required=True, help='输出CSV文件')
    parser.add_argument('--capacity', type=float, default=235.0, help='电池额定容量(Ah)')
    parser.add_argument('--init-soc', type=float, default=1.0, help='初始SOC(0.0~1.0)')
    args = parser.parse_args()

    logger.info(f"🚀 启动安时积分 SOC估计")
    logger.info(f"🔋 配置容量: {args.capacity}Ah, 初始SOC: {args.init_soc:.1%}")
    
    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        return
        
    res_df = run_estimators(args.input, args.capacity, args.init_soc)
    
    # ensure output dir exists
    out_dir = Path(args.output).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    
    res_df.to_csv(args.output, index=False)
    logger.info(f"✓ 结果已保存: {args.output}")
    logger.info(f"📊 最终SOC估计: {res_df['SOC'].iloc[-1]:.2%}")

if __name__ == '__main__':
    main()
