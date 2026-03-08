"""
I5.1 微网能量管理系统 - 核心算法实现

工商业微网综合能量管理，集成光伏、储能、负荷预测、电网交互等多维度优化。
支持多种运行模式：削峰填谷、需量控制、新能源消纳、应急备电。

主要功能：
1. 负荷预测（LSTM时间序列预测）
2. 光伏预测（基于天气预报）
3. 混合整数线性规划优化（MILP）
4. 实时修正控制
5. 经济效益分析
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy.optimize import milp, LinearConstraint, Bounds
import warnings

warnings.filterwarnings('ignore')


@dataclass
class StorageConfig:
    """储能系统配置"""
    capacity_kwh: float      # 电池容量 (kWh)
    max_power_kw: float      # 最大充放电功率 (kW)
    soc_min: float           # SOC下限
    soc_max: float           # SOC上限
    efficiency: float        # 循环效率 (0-1)
    cycle_life: int          # 循环寿命 (次)


@dataclass
class PVConfig:
    """光伏系统配置"""
    capacity_kw: float       # 装机容量 (kW)
    degradation_rate: float  # 年衰减率


@dataclass
class GridConfig:
    """电网配置"""
    max_import_kw: float     # 最大购电功率 (kW)
    max_export_kw: float     # 最大卖电功率 (kW)
    demand_charge_rate: float  # 需量电费 (元/kW/月)


@dataclass
class PriceConfig:
    """电价配置"""
    peak_price: float        # 峰电价 (元/kWh)
    valley_price: float      # 谷电价 (元/kWh)
    flat_price: float        # 平电价 (元/kWh)
    peak_hours: List[int]    # 峰时段 (小时)
    valley_hours: List[int]  # 谷时段 (小时)


@dataclass
class OptimizationResult:
    """优化结果"""
    timestamp: List[datetime]
    soc: np.ndarray
    p_charge: np.ndarray
    p_discharge: np.ndarray
    p_grid_import: np.ndarray
    p_grid_export: np.ndarray
    p_load: np.ndarray
    p_pv: np.ndarray
    total_cost: float
    total_carbon: float
    savings: float
    pv_self_consumption_rate: float


class LoadPredictor:
    """负荷预测器（简化版LSTM）"""

    def __init__(self, lookback: int = 168):
        self.lookback = lookback

    def predict(self, historical_load: pd.Series,
                forecast_horizon: int = 96) -> pd.Series:
        """
        负荷预测（简化版：基于历史模式和周期性）

        Args:
            historical_load: 历史负荷数据 (kW)
            forecast_horizon: 预测时长 (15分钟间隔)

        Returns:
            预测负荷序列
        """
        # 简化算法：使用历史同期平均值 + 趋势
        forecast = []
        base_load = historical_load.mean()

        for i in range(forecast_horizon):
            hour_of_day = (i // 4) % 24
            day_of_week = (i // 96) % 7

            # 模拟日模式（白天高，夜间低）
            daily_pattern = 1.0 + 0.3 * np.sin(2 * np.pi * (hour_of_day - 6) / 24)

            # 模拟周模式（工作日高，周末低）
            weekly_pattern = 1.0 if day_of_week < 5 else 0.7

            # 添加随机波动
            noise = np.random.normal(0, 0.05)

            predicted_load = base_load * daily_pattern * weekly_pattern * (1 + noise)
            forecast.append(max(predicted_load, 0))

        return pd.Series(forecast)


class PVPredictor:
    """光伏预测器"""

    def __init__(self, pv_config: PVConfig):
        self.config = pv_config

    def predict(self, date: datetime, forecast_horizon: int = 96) -> pd.Series:
        """
        光伏预测（基于日照模式）

        Args:
            date: 预测起始日期
            forecast_horizon: 预测时长 (15分钟间隔)

        Returns:
            预测光伏发电序列 (kW)
        """
        forecast = []

        for i in range(forecast_horizon):
            timestamp = date + timedelta(minutes=15*i)
            hour = timestamp.hour + timestamp.minute / 60

            # 日照模式：6:00-18:00有光照
            if 6 <= hour <= 18:
                # 正弦曲线模拟日照强度
                solar_intensity = np.sin(np.pi * (hour - 6) / 12)
                # 考虑云层遮挡（随机因素）
                cloud_factor = np.random.uniform(0.7, 1.0)
                pv_power = (self.config.capacity_kw *
                           solar_intensity *
                           cloud_factor)
            else:
                pv_power = 0

            forecast.append(max(pv_power, 0))

        return pd.Series(forecast)


class MicrogridOptimizer:
    """微网优化器（基于MILP）"""

    def __init__(self,
                 storage_config: StorageConfig,
                 pv_config: PVConfig,
                 grid_config: GridConfig,
                 price_config: PriceConfig):
        self.storage = storage_config
        self.pv = pv_config
        self.grid = grid_config
        self.price = price_config

    def get_price_at_hour(self, hour: int) -> float:
        """获取指定小时的电价"""
        if hour in self.price.peak_hours:
            return self.price.peak_price
        elif hour in self.price.valley_hours:
            return self.price.valley_price
        else:
            return self.price.flat_price

    def optimize(self,
                 load_forecast: pd.Series,
                 pv_forecast: pd.Series,
                 start_time: datetime,
                 initial_soc: float = 0.5,
                 dt: float = 0.25) -> OptimizationResult:
        """
        微网能量管理优化

        Args:
            load_forecast: 负荷预测 (kW)
            pv_forecast: 光伏预测 (kW)
            start_time: 优化起始时间
            initial_soc: 初始SOC
            dt: 时间步长 (小时)

        Returns:
            优化结果
        """
        T = len(load_forecast)
        n_vars = 4 * T  # P_charge, P_discharge, P_grid, SOC

        # 决策变量顺序：[P_charge, P_discharge, P_grid_import, P_grid_export, SOC]
        # 简化为：[P_charge, P_discharge, P_grid, SOC]
        # P_grid > 0 表示购电，P_grid < 0 表示卖电

        # 目标函数：最小化总成本
        # 电网购电成本
        c = np.zeros(4 * T)

        for t in range(T):
            hour = (start_time + timedelta(hours=t*dt)).hour
            price = self.get_price_at_hour(hour)
            c[t*4 + 2] = price * dt  # P_grid的系数

        # 约束条件
        A = []
        b = []
        lb = []
        ub = []

        # 1. 功率平衡约束：P_grid + P_pv + P_discharge = P_load + P_charge
        for t in range(T):
            row = np.zeros(4 * T)
            row[t*4 + 0] = 1    # P_charge
            row[t*4 + 1] = -1   # P_discharge (放电为正)
            row[t*4 + 2] = 1    # P_grid (购电为正)
            A.append(row)
            b.append(pv_forecast.iloc[t] - load_forecast.iloc[t])

        # 2. SOC动态约束
        # SOC[t+1] = SOC[t] + (P_charge * eff - P_discharge/eff) * dt / Capacity
        for t in range(T-1):
            row = np.zeros(4 * T)
            row[t*4 + 3] = -1  # SOC[t]
            row[(t+1)*4 + 3] = 1  # SOC[t+1]
            row[t*4 + 0] = -self.storage.efficiency * dt / self.storage.capacity_kwh  # P_charge
            row[t*4 + 1] = dt / (self.storage.efficiency * self.storage.capacity_kwh)  # P_discharge
            A.append(row)
            b.append(0)

        # 初始SOC约束
        row = np.zeros(4 * T)
        row[3] = 1
        A.append(row)
        b.append(initial_soc)

        # 3. 功率上下界
        for t in range(T):
            # P_charge: [0, max_power]
            lb.extend([0])
            ub.extend([self.storage.max_power_kw])

            # P_discharge: [0, max_power]
            lb.extend([0])
            ub.extend([self.storage.max_power_kw])

            # P_grid: [-max_export, max_import]
            lb.extend([-self.grid.max_export_kw])
            ub.extend([self.grid.max_import_kw])

            # SOC: [soc_min, soc_max]
            lb.extend([self.storage.soc_min])
            ub.extend([self.storage.soc_max])

        # 4. 互斥约束：不能同时充放电
        # 通过大M法实现：P_charge <= M * z, P_discharge <= M * (1-z)
        # 这里简化处理：在求解后处理

        # 转换约束矩阵
        A_matrix = np.array(A)
        b_vector = np.array(b)
        bounds = Bounds(lb, ub)

        # 求解MILP（简化为LP）
        try:
            from scipy.optimize import linprog
            res = linprog(c, A_eq=A_matrix, b_eq=b_vector, bounds=bounds,
                         method='highs')

            if not res.success:
                raise ValueError(f"优化失败: {res.message}")

            # 提取结果
            x = res.x

            # 后处理：确保不同时充放电
            p_charge = np.zeros(T)
            p_discharge = np.zeros(T)
            p_grid = np.zeros(T)
            soc = np.zeros(T)

            for t in range(T):
                charge = x[t*4 + 0]
                discharge = x[t*4 + 1]

                # 优先选择较大的操作
                if charge > discharge:
                    p_charge[t] = charge
                    p_discharge[t] = 0
                else:
                    p_charge[t] = 0
                    p_discharge[t] = discharge

                p_grid[t] = x[t*4 + 2]
                soc[t] = x[t*4 + 3]

            # 计算输出
            p_grid_import = np.maximum(p_grid, 0)
            p_grid_export = np.maximum(-p_grid, 0)

            # 计算总成本
            total_cost = 0
            for t in range(T):
                hour = (start_time + timedelta(hours=t*dt)).hour
                price = self.get_price_at_hour(hour)
                total_cost += p_grid_import[t] * price * dt

            # 计算节省（基准：无储能）
            baseline_cost = 0
            for t in range(T):
                hour = (start_time + timedelta(hours=t*dt)).hour
                price = self.get_price_at_hour(hour)
                net_load = max(load_forecast.iloc[t] - pv_forecast.iloc[t], 0)
                baseline_cost += net_load * price * dt

            # 光伏自用率
            pv_total = pv_forecast.sum() * dt
            pv_self_consumed = (pv_forecast * (1 - p_grid_export /
                                               (pv_forecast + p_discharge + 1e-6))).sum() * dt
            pv_self_consumption_rate = pv_self_consumed / max(pv_total, 1e-6)

            # 生成时间戳
            timestamp = [start_time + timedelta(hours=t*dt) for t in range(T)]

            return OptimizationResult(
                timestamp=timestamp,
                soc=soc,
                p_charge=p_charge,
                p_discharge=p_discharge,
                p_grid_import=p_grid_import,
                p_grid_export=p_grid_export,
                p_load=load_forecast.values,
                p_pv=pv_forecast.values,
                total_cost=total_cost,
                total_carbon=0,  # TODO: 添加碳排放计算
                savings=baseline_cost - total_cost,
                pv_self_consumption_rate=pv_self_consumption_rate
            )

        except Exception as e:
            print(f"优化求解错误: {e}")
            # 返回简单策略
            return self._fallback_strategy(load_forecast, pv_forecast,
                                           start_time, initial_soc, dt)

    def _fallback_strategy(self,
                          load_forecast: pd.Series,
                          pv_forecast: pd.Series,
                          start_time: datetime,
                          initial_soc: float,
                          dt: float) -> OptimizationResult:
        """备用策略：简单峰谷套利"""
        T = len(load_forecast)
        soc = np.zeros(T)
        p_charge = np.zeros(T)
        p_discharge = np.zeros(T)
        p_grid_import = np.zeros(T)
        p_grid_export = np.zeros(T)

        soc[0] = initial_soc

        for t in range(T):
            hour = (start_time + timedelta(hours=t*dt)).hour
            price = self.get_price_at_hour(hour)

            # 净负荷
            net_load = load_forecast.iloc[t] - pv_forecast.iloc[t]

            # 简单策略：谷时充电，峰时放电
            if price == self.price.valley_price and soc[t] < self.storage.soc_max:
                # 充电
                charge_power = min(self.storage.max_power_kw,
                                  (self.storage.soc_max - soc[t]) *
                                  self.storage.capacity_kwh / dt /
                                  self.storage.efficiency)
                p_charge[t] = charge_power
                soc[t] += charge_power * self.storage.efficiency * dt / self.storage.capacity_kwh
                net_load += charge_power

            elif price == self.price.peak_price and soc[t] > self.storage.soc_min:
                # 放电
                discharge_power = min(self.storage.max_power_kw,
                                     (soc[t] - self.storage.soc_min) *
                                     self.storage.capacity_kwh / dt *
                                     self.storage.efficiency,
                                     net_load)
                p_discharge[t] = discharge_power
                soc[t] -= discharge_power * dt / (self.storage.efficiency * self.storage.capacity_kwh)
                net_load -= discharge_power

            # 电网平衡
            if net_load > 0:
                p_grid_import[t] = min(net_load, self.grid.max_import_kw)
            else:
                p_grid_export[t] = min(-net_load, self.grid.max_export_kw)

            if t < T - 1:
                soc[t+1] = soc[t]

        return OptimizationResult(
            timestamp=[start_time + timedelta(hours=t*dt) for t in range(T)],
            soc=soc,
            p_charge=p_charge,
            p_discharge=p_discharge,
            p_grid_import=p_grid_import,
            p_grid_export=p_grid_export,
            p_load=load_forecast.values,
            p_pv=pv_forecast.values,
            total_cost=0,
            total_carbon=0,
            savings=0,
            pv_self_consumption_rate=0
        )


class MicrogridManager:
    """微网能量管理系统主类"""

    def __init__(self, config: Dict):
        """
        初始化微网管理器

        Args:
            config: 配置字典
        """
        self.storage = StorageConfig(**config['storage'])
        self.pv = PVConfig(**config['pv'])
        self.grid = GridConfig(**config['grid'])
        self.price = PriceConfig(**config['electricity_price'])

        self.load_predictor = LoadPredictor()
        self.pv_predictor = PVPredictor(self.pv)
        self.optimizer = MicrogridOptimizer(
            self.storage, self.pv, self.grid, self.price
        )

    def run_day_ahead_optimization(self,
                                   date: str,
                                   mode: str = "economic",
                                   initial_soc: float = 0.5) -> OptimizationResult:
        """
        运行日前优化

        Args:
            date: 日期 (YYYY-MM-DD)
            mode: 优化模式 (economic/carbon/reliability)
            initial_soc: 初始SOC

        Returns:
            优化结果
        """
        start_time = datetime.strptime(date, "%Y-%m-%d")
        horizon = 96  # 24小时，15分钟间隔

        # 生成预测数据
        # 在实际应用中，这里应该从数据库读取历史数据或调用预测API
        historical_load = pd.Series([500] * 168)  # 模拟历史负荷
        load_forecast = self.load_predictor.predict(historical_load, horizon)
        pv_forecast = self.pv_predictor.predict(start_time, horizon)

        # 运行优化
        result = self.optimizer.optimize(
            load_forecast,
            pv_forecast,
            start_time,
            initial_soc
        )

        return result

    def realtime_control(self,
                        current_time: str,
                        current_load: float,
                        current_pv: float,
                        current_soc: float) -> Dict:
        """
        实时控制

        Args:
            current_time: 当前时间
            current_load: 当前负荷 (kW)
            current_pv: 当前光伏 (kW)
            current_soc: 当前SOC

        Returns:
            控制指令
        """
        timestamp = datetime.strptime(current_time, "%Y-%m-%dT%H:%M:%S")
        hour = timestamp.hour
        price = self.get_price_at_hour(hour)

        net_load = current_load - current_pv

        action = "idle"
        target_power = 0

        # 简单控制策略
        if price == self.price.valley_price and current_soc < self.storage.soc_max:
            # 谷时充电
            action = "charge"
            target_power = self.storage.max_power_kw

        elif price == self.price.peak_price and current_soc > self.storage.soc_min:
            # 峰时放电
            action = "discharge"
            target_power = min(net_load, self.storage.max_power_kw)

        elif net_load > self.grid.max_import_kw:
            # 超过最大购电功率，放电补充
            if current_soc > self.storage.soc_min:
                action = "discharge"
                target_power = net_load - self.grid.max_import_kw

        return {
            "action": action,
            "target_power": target_power,
            "timestamp": current_time,
            "current_soc": current_soc,
            "net_load": net_load,
            "price": price
        }

    def get_price_at_hour(self, hour: int) -> float:
        """获取指定小时的电价"""
        return self.optimizer.get_price_at_hour(hour)


def main():
    """主函数 - 演示微网能量管理系统"""
    print("=" * 60)
    print("I5.1 微网能量管理系统")
    print("=" * 60)

    # 配置
    config = {
        'storage': {
            'capacity_kwh': 2000,
            'max_power_kw': 1000,
            'soc_min': 0.1,
            'soc_max': 0.9,
            'efficiency': 0.95,
            'cycle_life': 6000
        },
        'pv': {
            'capacity_kw': 1500,
            'degradation_rate': 0.005
        },
        'grid': {
            'max_import_kw': 2000,
            'max_export_kw': 1000,
            'demand_charge_rate': 40
        },
        'electricity_price': {
            'peak_price': 1.2,
            'valley_price': 0.4,
            'flat_price': 0.7,
            'peak_hours': [10, 11, 12, 13, 14, 15, 16, 17, 18],
            'valley_hours': [0, 1, 2, 3, 4, 5, 6, 22, 23]
        }
    }

    # 初始化管理器
    mgr = MicrogridManager(config)
    print("\n系统配置:")
    print(f"  储能容量: {config['storage']['capacity_kwh']} kWh")
    print(f"  最大功率: {config['storage']['max_power_kw']} kW")
    print(f"  光伏容量: {config['pv']['capacity_kw']} kW")
    print(f"  峰电价: {config['electricity_price']['peak_price']} 元/kWh")
    print(f"  谷电价: {config['electricity_price']['valley_price']} 元/kWh")

    # 运行日前优化
    print("\n" + "=" * 60)
    print("运行日前优化...")
    print("=" * 60)

    result = mgr.run_day_ahead_optimization(
        date="2025-03-08",
        mode="economic",
        initial_soc=0.3
    )

    print("\n优化结果:")
    print(f"  预计节省电费: {result.savings:.2f} 元")
    print(f"  光伏自用率: {result.pv_self_consumption_rate:.1%}")
    print(f"  总成本: {result.total_cost:.2f} 元")
    print(f"  平均SOC: {result.soc.mean():.2%}")

    # 显示前24个时间点（前6小时）
    print("\n前6小时调度计划:")
    print(f"{'时间':<16} {'负荷':<8} {'光伏':<8} {'充电':<8} {'放电':<8} {'SOC':<8}")
    for i in range(24):
        print(f"{result.timestamp[i].strftime('%Y-%m-%d %H:%M'):<16} "
              f"{result.p_load[i]:<8.1f} {result.p_pv[i]:<8.1f} "
              f"{result.p_charge[i]:<8.1f} {result.p_discharge[i]:<8.1f} "
              f"{result.soc[i]:<8.2%}")

    # 实时控制演示
    print("\n" + "=" * 60)
    print("实时控制演示...")
    print("=" * 60)

    control_action = mgr.realtime_control(
        current_time="2025-03-08T14:30:00",
        current_load=850,
        current_pv=320,
        current_soc=0.65
    )

    print("\n控制指令:")
    print(f"  动作: {control_action['action']}")
    print(f"  目标功率: {control_action['target_power']} kW")
    print(f"  净负荷: {control_action['net_load']} kW")
    print(f"  电价: {control_action['price']} 元/kWh")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
