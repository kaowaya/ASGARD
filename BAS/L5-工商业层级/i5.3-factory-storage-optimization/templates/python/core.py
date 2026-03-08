"""
I5.3 工厂配储优化系统 - 核心算法实现

工业用户侧储能配置与运行优化，基于工厂生产模式、负荷特性优化储能容量和运行策略。
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class StorageSizingResult:
    """储能配置结果"""
    capacity_kw: float
    capacity_kwh: float
    capex: float
    annual_savings: float
    payback_period: float
    irr: float
    npv: float


class FactoryStorageOptimizer:
    """工厂储能优化器"""

    def __init__(self, config: Dict):
        self.config = config

    def optimize_capacity(self,
                         load_profile: pd.Series,
                         price_schedule: Dict,
                         production_shifts: List[Dict],
                         capital_cost_yuan_per_kwh: float = 1200,
                         target_irr: float = 0.15) -> StorageSizingResult:
        """
        优化储能容量配置

        Args:
            load_profile: 负荷曲线 (kW)
            price_schedule: 电价表
            production_shifts: 生产班次
            capital_cost_yuan_per_kwh: 单位造价
            target_irr: 目标内部收益率

        Returns:
            优化配置结果
        """
        # 简化算法：基于峰谷价差和负荷特性

        # 计算峰谷负荷差
        peak_load = load_profile.max()
        valley_load = load_profile[load_profile < load_profile.quantile(0.3)].mean()

        # 估算最优容量
        optimal_power = (peak_load - valley_load) * 0.5
        optimal_energy = optimal_power * 2  # 2小时储能

        # 计算投资
        capex = optimal_energy * capital_cost_yuan_per_kwh

        # 估算年收益
        peak_hours = price_schedule.get('peak_hours', range(10, 18))
        valley_hours = price_schedule.get('valley_hours', range(0, 6))

        daily_savings = 0
        for hour in range(24):
            if hour in valley_hours:
                daily_savings += optimal_power * price_schedule['valley_price']
            elif hour in peak_hours:
                daily_savings += optimal_power * (price_schedule['peak_price'] -
                                                  price_schedule['valley_price'])

        annual_savings = daily_savings * 300  # 300个工作日

        # 计算回收期和IRR
        payback_period = capex / annual_savings
        irr = (annual_savings / capex) if capex > 0 else 0

        # 计算NPV（10年）
        discount_rate = 0.08
        npv = sum([annual_savings / ((1 + discount_rate) ** t)
                  for t in range(1, 11)]) - capex

        return StorageSizingResult(
            capacity_kw=optimal_power,
            capacity_kwh=optimal_energy,
            capex=capex,
            annual_savings=annual_savings,
            payback_period=payback_period,
            irr=irr,
            npv=npv
        )


def main():
    """演示"""
    print("I5.3 工厂配储优化系统")

    # 模拟负荷数据
    hours = 24
    base_load = np.array([500] * 8 + [1200] * 8 + [800] * 8)
    load_noise = np.random.normal(0, 50, hours)
    load_profile = pd.Series(base_load + load_noise)

    # 电价配置
    price_schedule = {
        'peak_price': 1.2,
        'valley_price': 0.4,
        'flat_price': 0.7,
        'peak_hours': list(range(10, 18)),
        'valley_hours': list(range(0, 6))
    }

    # 优化
    optimizer = FactoryStorageOptimizer({})
    result = optimizer.optimize_capacity(
        load_profile=load_profile,
        price_schedule=price_schedule,
        production_shifts=[{'start': 8, 'end': 18}]
    )

    print(f"\n优化结果:")
    print(f"  最优功率: {result.capacity_kw:.0f} kW")
    print(f"  最优容量: {result.capacity_kwh:.0f} kWh")
    print(f"  总投资: {result.capex:.0f} 元")
    print(f"  年收益: {result.annual_savings:.0f} 元")
    print(f"  回收期: {result.payback_period:.2f} 年")
    print(f"  IRR: {result.irr:.1%}")
    print(f"  NPV(10年): {result.npv:.0f} 元")


if __name__ == "__main__":
    main()
