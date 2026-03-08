# templates/python/pipeline.py
"""
ASGARD L3-Cloud Data Pipeline
工业级时序异常数据清洗与特征提取器

Usage:
    python pipeline.py --input data.csv --output clean_features.csv --freq 1S
"""

import argparse
import logging
import pandas as pd
import numpy as np
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class CloudDataPipeline:
    def __init__(self, target_freq='10S', max_gap_seconds=900, 
                 v_min=2.0, v_max=4.5, temp_min=-40, temp_max=85):
        self.freq = target_freq # 重采样频率
        self.max_gap = max_gap_seconds # 切割长断点连续数据段阈值 (默认15min)
        
        # 物理边界约束
        self.v_min = v_min
        self.v_max = v_max
        self.temp_min = temp_min
        self.temp_max = temp_max
        
    def _clean_outliers(self, df):
        """绝对物理边界毛刺过滤"""
        df = df.copy()
        
        # 将超出物理范围的值设为 NaN (后续处理插值)
        v_mask = (df['voltage'] < self.v_min) | (df['voltage'] > self.v_max)
        if v_mask.any():
            logger.warning(f"剔除了 {v_mask.sum()} 个电压超出物理边界的离群点")
            df.loc[v_mask, 'voltage'] = np.nan
            
        t_mask = (df['temperature'] < self.temp_min) | (df['temperature'] > self.temp_max)
        if t_mask.any():
            df.loc[t_mask, 'temperature'] = np.nan
            
        return df
        
    def _zscore_spike_removal(self, series, window=5, threshold=3):
        """利用滑动窗口的中位数绝对偏差(MAD) 或 Z-Score 移除突变尖峰"""
        # 为了高效，这里简单的使用 rolling median 偏差
        roll_med = series.rolling(window, center=True, min_periods=1).median()
        diff = np.abs(series - roll_med)
        # 用滚动标准差的一定倍数作为阈值，或者简单的固定物理突变(比如一步变0.5V)
        # 此处使用简单的固定突变阈值 (比如 0.5V/Step 是异常)
        spike_mask = diff > 0.5 
        series_clean = series.copy()
        series_clean[spike_mask] = np.nan
        return series_clean

    def process(self, df, time_col='timestamp'):
        """执行端到端的清洗与特征提取管线"""
        logger.info(f"开始清洗，原始数据条数: {len(df)}")
        
        # 1. 解析时间 & 去重排序
        # 强制转换为数值以防CSV里带字符串
        numeric_time = pd.to_numeric(df[time_col], errors='coerce')
        if numeric_time.notna().sum() > len(df) * 0.5: # 绝大多数是数值(unix ts)
            df[time_col] = pd.to_datetime(numeric_time, unit='s')
        else:
            df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
        
        df = df.sort_values(by=time_col)
        df = df.drop_duplicates(subset=[time_col], keep='last')
        df = df.set_index(time_col)
        
        # 2. 移除违背物理常识的毛刺
        df = self._clean_outliers(df)
        df['voltage'] = self._zscore_spike_removal(df['voltage'])
        
        # 3. 按时间间隔切分连续片段 (Segment Extraction)
        # 如果断点超过 max_gap，打上不同的 segment_id
        time_diffs = df.index.to_series().diff().dt.total_seconds()
        segment_breaks = time_diffs > self.max_gap
        df['segment_id'] = segment_breaks.cumsum().fillna(0).astype('int64')
        
        logger.info(f"检测到 {df['segment_id'].nunique()} 个独立有效运行时间段(Segment)")
        
        # 4. 基于频率的重采样 (Resampling & Interpolation)
        # 这是为了对齐不规则的上报。在每个 Segment 内部进行独立的重采样
        def resample_segment(segment_df):
            # 取出需要处理的列
            cols = ['current', 'voltage', 'temperature', 'segment_id']
            # 将这个Segment重采样到固定的格子上
            res = segment_df[cols].resample(self.freq).mean()
            
            # 对电压/温度用线性插值
            res['voltage'] = res['voltage'].interpolate(method='time', limit=5)
            res['temperature'] = res['temperature'].interpolate(method='time', limit=5)
            
            # 电流使用就近前向填充或抛弃（视具体业务逻辑，此处前向填充）
            res['current'] = res['current'].ffill(limit=3).fillna(0)
            res['segment_id'] = res['segment_id'].ffill()
            return res.dropna(subset=['voltage']) # 扔掉实在没救的空洞
            
        clean_df = df.groupby('segment_id', group_keys=False).apply(resample_segment)

        if len(clean_df) == 0:
            logger.error("数据完全不可用！全是断点与空洞。")
            return clean_df
            
        # 5. 高级特征衍生 (Feature Engineering 矢量化)
        # 计算时间步长(秒)用于微分
        # 因为重采样过了，理论上 dt 都是恒定的 (例如 freq='1S' dt=1)
        freq_seconds = pd.to_timedelta(self.freq).total_seconds()
        
        # 求导特征 (按分组求，防止跨Segment跳变)
        for segment_name, group in clean_df.groupby('segment_id'):
            # dV/dt (V/s)
            clean_df.loc[group.index, 'dV_dt'] = group['voltage'].diff() / freq_seconds
            # dT/dt (°C/s)
            clean_df.loc[group.index, 'dT_dt'] = group['temperature'].diff() / freq_seconds
            # dI/dt (A/s)
            clean_df.loc[group.index, 'dI_dt'] = group['current'].diff() / freq_seconds
        
        # 填充差分产生的头部第一行NaN为0
        feature_cols = ['dV_dt', 'dT_dt', 'dI_dt']
        clean_df[feature_cols] = clean_df[feature_cols].fillna(0)
        
        logger.info(f"清洗完成，输出等频矩阵条数: {len(clean_df)}")
        # 恢复index为一列时间戳
        clean_df = clean_df.reset_index()
        return clean_df


def main():
    parser = argparse.ArgumentParser(description='Cloud Data Preprocessing Pipeline')
    parser.add_argument('--input', required=True, help='输入脏杂时序数据CSV')
    parser.add_argument('--output', required=True, help='输出特征矩阵CSV')
    parser.add_argument('--freq', default='1S', help='清洗重采样频率, 如 1S, 10S')
    parser.add_argument('--col-vol', default='voltage', help='原始数据中的电压列名')
    parser.add_argument('--col-cur', default='current', help='原始数据中的电流列名')
    parser.add_argument('--col-temp', default='temperature', help='原始数据中的温度列名')
    parser.add_argument('--v-min', type=float, default=0.0, help='电压下限(默认0.0V,防反接,兼容Pack)')
    parser.add_argument('--v-max', type=float, default=1000.0, help='电压上限(默认1000V,兼容储能高压簇/Pack)')
    parser.add_argument('--t-min', type=float, default=-40.0, help='温度下限')
    parser.add_argument('--t-max', type=float, default=85.0, help='温度上限')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        return
        
    df_raw = pd.read_csv(args.input, comment='#')
    
    # 统一列名映射为内部标准名称
    rename_mapping = {
        args.col_vol: 'voltage',
        args.col_cur: 'current',
        args.col_temp: 'temperature'
    }
    rename_valid = {k:v for k,v in rename_mapping.items() if k in df_raw.columns}
    df_raw = df_raw.rename(columns=rename_valid)
    
    pipeline = CloudDataPipeline(
        target_freq=args.freq,
        v_min=args.v_min,
        v_max=args.v_max,
        temp_min=args.t_min,
        temp_max=args.t_max
    )
    
    df_clean = pipeline.process(df_raw, time_col='timestamp')
    
    out_dir = Path(args.output).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(args.output, index=False)
    logger.info(f"💾 特征矩阵已保存到: {args.output}")

if __name__ == '__main__':
    main()
