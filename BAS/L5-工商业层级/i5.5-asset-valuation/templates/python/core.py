"""
I5.5 储能电站资产评估系统 - 核心算法实现

储能电站资产价值评估，综合考虑技术性能、衰减趋势、市场环境进行动态估值。
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ValuationResult:
    """估值结果"""
    asset_value_yuan: float
    remaining_life_years: float
    technical_risk_level: str
    economic_risk_level: str
    projected_revenue_10y: float
    npv: float
    irr: float


class AssetValuator:
    """资产估值器"""

    def __init__(self, config: Dict):
        self.config = config

    def evaluate(self,
                station_id: str,
                technical_data: Dict,
                market_forecast: Dict) -> ValuationResult:
        """
        综合资产评估

        Args:
            station_id: 电站ID
            technical_data: 技术数据（SOH、循环次数等）
            market_forecast: 市场预测（电价、辅助服务等）

        Returns:
            估值结果
        """
        # 1. 评估技术价值
        soh = technical_data.get('soh', 0.95)
        cycles = technical_data.get('cycles', 1000)
        rated_cycles = technical_data.get('rated_cycles', 6000)

        # 剩余寿命（年）
        remaining_cycles = rated_cycles - cycles
        daily_cycles = 1.0
        remaining_life_years = remaining_cycles / (daily_cycles * 365)

        # 2. 预测收益
        capacity_kwh = technical_data.get('capacity_kwh', 2000)
        power_kw = technical_data.get('power_kw', 1000)

        # 年收益估算（简化）
        annual_arbitrage_revenue = capacity_kwh * 365 * 0.5 * 0.8  # 日循环1次，价差0.8元
        annual_auxiliary_revenue = power_kw * 60 * 12  # 调频收益

        projected_revenue_10y = (annual_arbitrage_revenue + annual_auxiliary_revenue) * 10

        # 3. 计算资产价值（DCF方法）
        discount_rate = 0.10
        residual_value = capacity_kwh * 200 * 0.1  # 残值

        pv_revenue = sum([
            (annual_arbitrage_revenue + annual_auxiliary_revenue) / ((1 + discount_rate) ** t)
            for t in range(1, 11)
        ])

        pv_residual = residual_value / ((1 + discount_rate) ** 10)
        asset_value_yuan = pv_revenue + pv_residual

        # 4. 风险评估
        technical_risk_level = self._assess_technical_risk(soh, cycles, rated_cycles)
        economic_risk_level = self._assess_economic_risk(market_forecast)

        # 5. 计算IRR和NPV
        initial_investment = capacity_kwh * 1200  # 1200元/kWh
        npv = asset_value_yuan - initial_investment

        # 简化IRR计算
        if initial_investment > 0:
            irr = ((annual_arbitrage_revenue + annual_auxiliary_revenue) / initial_investment)
        else:
            irr = 0

        return ValuationResult(
            asset_value_yuan=asset_value_yuan,
            remaining_life_years=remaining_life_years,
            technical_risk_level=technical_risk_level,
            economic_risk_level=economic_risk_level,
            projected_revenue_10y=projected_revenue_10y,
            npv=npv,
            irr=irr
        )

    def _assess_technical_risk(self, soh: float, cycles: int, rated_cycles: int) -> str:
        """评估技术风险"""
        if soh > 0.9 and cycles < rated_cycles * 0.3:
            return "Low"
        elif soh > 0.8 and cycles < rated_cycles * 0.6:
            return "Medium"
        else:
            return "High"

    def _assess_economic_risk(self, market_forecast: Dict) -> str:
        """评估经济风险"""
        volatility = market_forecast.get('price_volatility', 0.2)

        if volatility < 0.15:
            return "Low"
        elif volatility < 0.3:
            return "Medium"
        else:
            return "High"


def main():
    """演示"""
    print("I5.5 储能电站资产评估系统")

    valuator = AssetValuator({})

    # 模拟数据
    technical_data = {
        'soh': 0.92,
        'cycles': 1500,
        'rated_cycles': 6000,
        'capacity_kwh': 2000,
        'power_kw': 1000
    }

    market_forecast = {
        'price_volatility': 0.2
    }

    # 评估
    result = valuator.evaluate(
        station_id="STATION_001",
        technical_data=technical_data,
        market_forecast=market_forecast
    )

    print(f"\n估值结果:")
    print(f"  资产价值: {result.asset_value_yuan/10000:.1f} 万元")
    print(f"  剩余寿命: {result.remaining_life_years:.1f} 年")
    print(f"  10年预期收益: {result.projected_revenue_10y/10000:.1f} 万元")
    print(f"  NPV: {result.npv/10000:.1f} 万元")
    print(f"  IRR: {result.irr:.1%}")
    print(f"  技术风险: {result.technical_risk_level}")
    print(f"  经济风险: {result.economic_risk_level}")


if __name__ == "__main__":
    main()
