# templates/python/sos_diagnosis.py
"""
ASGARD L3-Cloud: 内短路诊断 - SOS (Safety Gene)
基于基因图谱的内短路早期诊断。

Usage:
    python sos_diagnosis.py --input ../c3-0-data-pipeline/data_samples/output/clean_features.csv --output data_samples/output/sos_report.json
"""

import argparse
import logging
import json
import numpy as np
import pandas as pd
from scipy.stats import entropy
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class SafetyGeneISC:
    def __init__(self, bins=20):
        self.bins = bins # 香农熵用的直方图分箱数
        
    def _calc_shannon_entropy(self, series):
        """计算一维连续变量分布的香农熵 (bits)"""
        # 抛弃 NaN
        valid_data = series.dropna()
        if len(valid_data) < 10:
            return 3.5 # 数据太少，默认正常(高熵)以防误报
            
        # 1. 归一化并分箱求概率密度
        hist, _ = np.histogram(valid_data, bins=self.bins, density=True)
        # 将概率密度转化为离散概率(加上微小值防log(0))
        p = hist / hist.sum()
        p = p + 1e-9
        p = p / p.sum()
        
        # 2. 计算熵
        H = entropy(p, base=2)
        return float(H)
        
    def extract_genes(self, df):
        """从清洗后的标准DataFrame中提取基因矩阵特征"""
        genes = {}
        
        # g1: 电压香农熵 (正常>3.0, 短路<2.5)
        # 短路的电芯电压会趋向同质低位，分布变窄
        genes['g1_voltage_entropy'] = self._calc_shannon_entropy(df['voltage'])
        
        # g2: 最大温升梯度 (dT/dt)
        if 'dT_dt' in df.columns:
            genes['g2_max_dTdt'] = float(df['dT_dt'].max())
        else:
            genes['g2_max_dTdt'] = 0.0
            
        # g3: 均方根电流变化率 (反映工况剧烈程度，用于置信度评估)
        if 'dI_dt' in df.columns:
            genes['g3_current_mad'] = float(np.mean(np.abs(df['dI_dt'].dropna())))
        else:
            genes['g3_current_mad'] = 0.0
            
        # g4: 纯静置期压降 (模拟自放电 dV_dt)
        # 筛选条件：电流在完全0附近 (静置)，取这段时间的平均压降率
        rest_mask = np.abs(df['current']) <= 0.5
        rest_df = df[rest_mask]
        if len(rest_df) > 10 and 'dV_dt' in rest_df.columns:
            genes['g4_rest_voltage_drift'] = float(rest_df['dV_dt'].mean())
        else:
            genes['g4_rest_voltage_drift'] = 0.0
            
        return genes
        
    def diagnose(self, genes):
        """融合打分 (极简专家系统权重)"""
        score = 0.0
        details = []
        
        # 1. 熵判断
        g1 = genes.get('g1_voltage_entropy', 3.5)
        if g1 < 2.5:
            score += 0.4
            details.append("电压分布熵极低(聚集)，疑似漏电拖拽。")
        elif g1 < 3.0:
            score += 0.2
            details.append("电压分布熵偏低，一致性散开前期。")
            
        # 2. 温升判断 (异常发热)
        g2 = genes.get('g2_max_dTdt', 0.0)
        # 假设重采样是1s，0.1 degree/s 即 1度/10秒，非常危险
        if g2 > 0.1:
            score += 0.4
            details.append(f"检出剧烈温升事件(MAX={g2:.3f}°C/s)。")
            
        # 3. 静置泄露倒流
        g4 = genes.get('g4_rest_voltage_drift', 0.0)
        # 负值表示掉压。正常电芯静置极化恢复后应该平稳。
        if g4 < -0.005: # -5mV/s
            score += 0.3
            details.append(f"强烈静置期压降漏电({g4*1000:.1f}mV/s)。")
            
        final_score = min(score, 1.0)
        
        return {
            'is_abnormal': final_score >= 0.6,
            'risk_level': round(final_score, 3),
            'fault_type': 'Internal Short Circuit (Micro)' if final_score >= 0.6 else 'Normal',
            'confidence': round(1.0 - (genes.get('g3_current_mad', 0) / 100.0), 2), # 剧烈工况下置信度低
            'genes': genes,
            'diagnostics_msg': " | ".join(details) if details else "指标正常"
        }

def process_file(input_csv, output_json):
    df = pd.read_csv(input_csv)
    
    detector = SafetyGeneISC(bins=20)
    genes = detector.extract_genes(df)
    result = detector.diagnose(genes)
    
    logger.info("=== SOS基因诊断报告 ===")
    logger.info(f"Risk Level: {result['risk_level']}")
    logger.info(f"Is Abnormal: {result['is_abnormal']}")
    logger.info(f"Message: {result['diagnostics_msg']}")
    
    out_dir = Path(output_json).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    logger.info(f"报告已保存至 {output_json}")

def main():
    parser = argparse.ArgumentParser(description='Cloud ISC Diagnosis - SOS Gene')
    parser.add_argument('--input', required=True, help='输入的清洗后特征矩阵CSV')
    parser.add_argument('--output', required=True, help='输出的JSON诊断报告文件')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        return
        
    process_file(args.input, args.output)

if __name__ == '__main__':
    main()
