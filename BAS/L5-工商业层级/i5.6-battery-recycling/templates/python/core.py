"""
I5.6 电池回收决策系统 - 核心算法实现

退役动力电池梯次利用与回收决策，评估健康状态、经济价值、环境影响。
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class RecyclingDecision:
    """回收决策"""
    recommendation: str  # cascading/recycling
    target_scenario: str
    estimated_value_yuan: float
    co2_reduction_kg: float
    remaining_life_years: float
    confidence: float


class RecyclingDecisionEngine:
    """电池回收决策引擎"""

    def __init__(self, config: Dict):
        self.config = config

        # 材料市场价格（元/kg）
        self.material_prices = {
            'lithium': 150,
            'nickel': 120,
            'cobalt': 350,
            'manganese': 40,
            'iron': 5,
            'aluminum': 20
        }

        # 电池材料组成（kg/kWh）
        self.battery_composition = {
            'NCM': {'lithium': 0.12, 'nickel': 0.45, 'cobalt': 0.15, 'manganese': 0.10},
            'LFP': {'lithium': 0.10, 'iron': 0.35, 'phosphorus': 0.30}
        }

    def evaluate(self,
                battery_id: str,
                soh: float,
                cycles: int,
                battery_type: str,
                capacity_kwh: float = 60) -> RecyclingDecision:
        """
        评估退役电池处理方案

        Args:
            battery_id: 电池ID
            soh: 健康状态 (0-1)
            cycles: 循环次数
            battery_type: 电池类型 (NCM/LFP)
            capacity_kwh: 电池容量

        Returns:
            决策结果
        """
        # 1. 评估梯次利用价值
        cascading_feasible, cascading_value, cascading_co2 = self._evaluate_cascading(
            soh, cycles, battery_type, capacity_kwh
        )

        # 2. 评估回收价值
        recycling_value, recycling_co2 = self._evaluate_recycling(
            battery_type, capacity_kwh
        )

        # 3. 综合决策
        if cascading_feasible and cascading_value > recycling_value:
            recommendation = 'cascading'
            target_scenario = self._match_scenario(soh, capacity_kwh)
            estimated_value = cascading_value
            co2_reduction = cascading_co2
            remaining_life = self._estimate_remaining_life(soh, cycles)
            confidence = 0.85 if soh > 0.7 else 0.70
        else:
            recommendation = 'recycling'
            target_scenario = 'material_recovery'
            estimated_value = recycling_value
            co2_reduction = recycling_co2
            remaining_life = 0
            confidence = 0.95

        return RecyclingDecision(
            recommendation=recommendation,
            target_scenario=target_scenario,
            estimated_value_yuan=estimated_value,
            co2_reduction_kg=co2_reduction,
            remaining_life_years=remaining_life,
            confidence=confidence
        )

    def _evaluate_cascading(self, soh: float, cycles: int,
                           battery_type: str, capacity_kwh: float) -> tuple:
        """评估梯次利用"""
        # 技术可行性
        feasible = soh >= 0.6 and cycles < 4000

        if not feasible:
            return False, 0, 0

        # 经济价值
        remaining_capacity = capacity_kwh * soh
        refurbishment_cost = 50 * capacity_kwh  # 翻新成本
        cascading_price = 300 * remaining_capacity  # 梯次利用价格

        value = max(0, cascading_price - refurbishment_cost)

        # 碳减排（相比新电池）
        co2_reduction = capacity_kwh * 100  # kg CO2/kWh

        return feasible, value, co2_reduction

    def _evaluate_recycling(self, battery_type: str, capacity_kwh: float) -> tuple:
        """评估材料回收"""
        composition = self.battery_composition.get(battery_type, {})

        total_value = 0
        total_mass = 0

        for material, ratio in composition.items():
            if material in self.material_prices:
                mass = capacity_kwh * ratio * 10  # 估算质量
                recovery_rate = 0.90  # 回收率
                value = mass * recovery_rate * self.material_prices[material]
                total_value += value
                total_mass += mass

        # 回收成本
        recycling_cost = 20 * total_mass  # 20元/kg
        value = max(0, total_value - recycling_cost)

        # 碳减排
        co2_reduction = capacity_kwh * 50  # kg CO2

        return value, co2_reduction

    def _match_scenario(self, soh: float, capacity_kwh: float) -> str:
        """匹配梯次利用场景"""
        if soh >= 0.8:
            if capacity_kwh >= 100:
                return 'industrial_storage'
            else:
                return 'residential_storage'
        elif soh >= 0.7:
            return 'low_speed_vehicle'
        else:
            return 'backup_power'

    def _estimate_remaining_life(self, soh: float, cycles: int) -> float:
        """估算剩余寿命（年）"""
        remaining_capacity_loss = soh - 0.6  # 假设60%为寿命终点
        annual_degradation = 0.03  # 年衰减率

        return max(0, remaining_capacity_loss / annual_degradation)


def main():
    """演示"""
    print("I5.6 电池回收决策系统")

    engine = RecyclingDecisionEngine({})

    # 案例1：可梯次利用
    decision1 = engine.evaluate(
        battery_id="BATT_001",
        soh=0.78,
        cycles=2200,
        battery_type="NCM",
        capacity_kwh=60
    )

    print(f"\n案例1 - 电池BATT_001 (SOH={decision1.confidence:.0%}):")
    print(f"  推荐方案: {decision1.recommendation}")
    print(f"  应用场景: {decision1.target_scenario}")
    print(f"  预期价值: {decision1.estimated_value_yuan:.0f} 元")
    print(f"  碳减排: {decision1.co2_reduction_kg:.0f} kg")
    print(f"  剩余寿命: {decision1.remaining_life_years:.1f} 年")

    # 案例2：需回收
    decision2 = engine.evaluate(
        battery_id="BATT_002",
        soh=0.55,
        cycles=4500,
        battery_type="NCM",
        capacity_kwh=60
    )

    print(f"\n案例2 - 电池BATT_002 (SOH=55%):")
    print(f"  推荐方案: {decision2.recommendation}")
    print(f"  预期价值: {decision2.estimated_value_yuan:.0f} 元")
    print(f"  碳减排: {decision2.co2_reduction_kg:.0f} kg")


if __name__ == "__main__":
    main()
