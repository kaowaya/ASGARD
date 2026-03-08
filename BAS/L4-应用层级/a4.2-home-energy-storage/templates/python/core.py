"""
A4.2-家庭储能优化核心实现

该模块提供家庭能源管理系统的核心算法，包括：
1. 光伏发电预测与优化
2. 储能充放电调度
3. 负荷智能管理
4. 峰谷电价套利
5. 备用电源模式

Author: ASGARD
Version: 1.0.0
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum


class LoadPriority(Enum):
    """负载优先级"""
    CRITICAL = 1  # 关键负载（医疗、安全）
    HIGH = 2      # 高优先级（照明、冰箱）
    MEDIUM = 3    # 中优先级（空调、洗衣机）
    LOW = 4       # 低优先级（电动车慢充）
    FLEXIBLE = 5  # 灵活负载（泳池泵、热水器）


@dataclass
class SolarGeneration:
    """光伏发电数据"""
    capacity_kw: float  # 光伏装机容量
    efficiency: float = 0.18  # 组件效率
    degradation: float = 0.005  # 年衰减率
    forecast: Optional[np.ndarray] = None  # 发电预测 (kW)


@dataclass
class BatteryStorage:
    """储能电池数据"""
    capacity_kwh: float
    current_soc: float  # %
    max_charge_power: float  # kW
    max_discharge_power: float  # kW
    charge_efficiency: float = 0.95
    discharge_efficiency: float = 0.95
    battery_type: str = 'LFP'


@dataclass
class HouseholdLoad:
    """家庭负载数据"""
    name: str
    power_rating: float  # kW
    controllable: bool
    priority: LoadPriority
    energy_demand: Optional[float] = None  # kWh
    time_window: Optional[Tuple[int, int]] = None
    forecast: Optional[np.ndarray] = None  # 负荷预测 (kW)


@dataclass
class EnergySchedule:
    """能量调度计划"""
    solar_to_load: np.ndarray  # kW
    solar_to_battery: np.ndarray  # kW
    solar_to_grid: np.ndarray  # kW
    battery_to_load: np.ndarray  # kW
    grid_to_load: np.ndarray  # kW
    grid_to_battery: np.ndarray  # kW
    battery_soc: np.ndarray  # %


@dataclass
class OptimizationResult:
    """优化结果"""
    schedule: EnergySchedule
    cost_analysis: Dict
    performance_metrics: Dict
    load_schedule: Dict
    recommendations: Dict


class HomeEnergyOptimizer:
    """
    家庭能源优化器

    实现光伏、储能、负载和电网的最优协同调度
    """

    def __init__(
        self,
        solar: SolarGeneration,
        battery: BatteryStorage,
        loads: List[HouseholdLoad],
        price_schedule: List[float]
    ):
        """
        初始化优化器

        Args:
            solar: 光伏发电系统
            battery: 储能电池系统
            loads: 家庭负载列表
            price_schedule: 24小时电价 (¢/kWh)
        """
        self.solar = solar
        self.battery = battery
        self.loads = loads
        self.prices = np.array(price_schedule)
        self.time_horizon = 24  # 24小时

    def optimize(
        self,
        mode: str = 'economic',  # 'economic', 'self_sufficiency', 'backup'
        backup_hours: float = 4.0,
        export_limit: float = 10.0
    ) -> OptimizationResult:
        """
        执行能源优化

        Args:
            mode: 优化模式
            backup_hours: 备用时长（小时）
            export_limit: 上网功率限制 (kW)

        Returns:
            OptimizationResult: 优化结果
        """
        # 生成光伏发电预测
        pv_forecast = self._generate_pv_forecast()

        # 生成负荷预测
        load_forecast = self._generate_load_forecast()

        # 根据模式优化
        if mode == 'economic':
            schedule = self._optimize_economic(pv_forecast, load_forecast, export_limit)
        elif mode == 'self_sufficiency':
            schedule = self._optimize_self_sufficiency(pv_forecast, load_forecast)
        elif mode == 'backup':
            schedule = self._optimize_backup(pv_forecast, load_forecast, backup_hours)
        else:
            raise ValueError(f"Unknown optimization mode: {mode}")

        # 计算成本分析
        cost_analysis = self._calculate_costs(schedule)

        # 计算性能指标
        performance = self._calculate_performance(schedule, pv_forecast, load_forecast)

        # 负载调度计划
        load_schedule = self._schedule_loads(schedule, load_forecast)

        # 生成建议
        recommendations = self._generate_recommendations(schedule, performance)

        return OptimizationResult(
            schedule=schedule,
            cost_analysis=cost_analysis,
            performance_metrics=performance,
            load_schedule=load_schedule,
            recommendations=recommendations
        )

    def _generate_pv_forecast(self) -> np.ndarray:
        """生成光伏发电预测"""
        if self.solar.forecast is not None:
            return self.solar.forecast

        # 简化模型：基于太阳位置
        hours = np.arange(self.time_horizon)
        # 典型晴天发电曲线（正态分布）
        peak_hour = 13  # 13:00峰值
        spread = 3.5
        pv_profile = self.solar.capacity_kw * np.exp(
            -0.5 * ((hours - peak_hour) / spread) ** 2
        )
        # 夜间发电为0
        pv_profile[hours < 6] = 0
        pv_profile[hours > 19] = 0

        return pv_profile

    def _generate_load_forecast(self) -> np.ndarray:
        """生成负荷预测"""
        if all(load.forecast is not None for load in self.loads):
            return sum(load.forecast for load in self.loads)

        # 简化模型：典型家庭负荷曲线
        hours = np.arange(self.time_horizon)
        base_load = 0.3  # 基础负荷 300W

        # 晨峰（7-9点）
        morning_peak = 1.5 * np.exp(-0.5 * ((hours - 8) / 1.5) ** 2)
        # 晚峰（18-22点）
        evening_peak = 2.5 * np.exp(-0.5 * ((hours - 20) / 2.5) ** 2)

        load_profile = base_load + morning_peak + evening_peak

        return load_profile

    def _optimize_economic(
        self,
        pv_forecast: np.ndarray,
        load_forecast: np.ndarray,
        export_limit: float
    ) -> EnergySchedule:
        """经济最优模式"""
        n = self.time_horizon

        # 初始化调度数组
        solar_to_load = np.zeros(n)
        solar_to_battery = np.zeros(n)
        solar_to_grid = np.zeros(n)
        battery_to_load = np.zeros(n)
        grid_to_load = np.zeros(n)
        grid_to_battery = np.zeros(n)
        battery_soc = np.zeros(n + 1)
        battery_soc[0] = self.battery.current_soc

        for i in range(n):
            # 优先使用光伏满足负载
            solar_available = pv_forecast[i]
            load_demand = load_forecast[i]

            # 光伏 -> 负载
            solar_to_load[i] = min(solar_available, load_demand)
            remaining_solar = solar_available - solar_to_load[i]
            remaining_load = load_demand - solar_to_load[i]

            # 光伏 -> 电池（如果有剩余）
            if remaining_solar > 0:
                # 检查电池是否能充电
                soc_percent = battery_soc[i]
                if soc_percent < 90:  # 最高90% SOC
                    available_capacity = (90 - soc_percent) / 100 * self.battery.capacity_kwh
                    max_charge = min(
                        remaining_solar,
                        self.battery.max_charge_power,
                        available_capacity
                    )
                    solar_to_battery[i] = max_charge
                    remaining_solar -= max_charge

            # 剩余光伏 -> 电网
            solar_to_grid[i] = min(remaining_solar, export_limit)

            # 如果负载未满足，使用电池放电
            if remaining_load > 0:
                soc_percent = battery_soc[i]
                if soc_percent > 20:  # 最低20% SOC
                    available_energy = (soc_percent - 20) / 100 * self.battery.capacity_kwh
                    max_discharge = min(
                        remaining_load,
                        self.battery.max_discharge_power,
                        available_energy
                    )

                    # 在高电价时段优先放电
                    price_rank = np.argsort(self.prices).tolist().index(i)
                    if price_rank >= 16:  # 高电价时段（前8个最贵时段）
                        battery_to_load[i] = max_discharge
                        remaining_load -= max_discharge

            # 如果负载仍未满足，从电网购电
            if remaining_load > 0:
                grid_to_load[i] = remaining_load

            # 在低电价时段从电网充电
            price_rank = np.argsort(self.prices).tolist().index(i)
            if price_rank < 8:  # 低电价时段（前8个最便宜时段）
                soc_percent = battery_soc[i]
                if soc_percent < 80:
                    # 计算需要充电多少（充到80%）
                    target_energy = (80 - soc_percent) / 100 * self.battery.capacity_kwh
                    max_charge = min(
                        self.battery.max_charge_power,
                        target_energy
                    )
                    grid_to_battery[i] = max_charge

            # 更新SOC
            energy_change = (
                solar_to_battery[i] * self.battery.charge_efficiency +
                grid_to_battery[i] * self.battery.charge_efficiency -
                battery_to_load[i] / self.battery.discharge_efficiency
            )
            battery_soc[i + 1] = battery_soc[i] + energy_change / self.battery.capacity_kwh * 100

        return EnergySchedule(
            solar_to_load=solar_to_load,
            solar_to_battery=solar_to_battery,
            solar_to_grid=solar_to_grid,
            battery_to_load=battery_to_load,
            grid_to_load=grid_to_load,
            grid_to_battery=grid_to_battery,
            battery_soc=battery_soc[:-1]
        )

    def _optimize_self_sufficiency(
        self,
        pv_forecast: np.ndarray,
        load_forecast: np.ndarray
    ) -> EnergySchedule:
        """自给自足模式 - 最大化自发自用"""
        n = self.time_horizon

        # 初始化
        solar_to_load = np.zeros(n)
        solar_to_battery = np.zeros(n)
        solar_to_grid = np.zeros(n)
        battery_to_load = np.zeros(n)
        grid_to_load = np.zeros(n)
        grid_to_battery = np.zeros(n)
        battery_soc = np.zeros(n + 1)
        battery_soc[0] = self.battery.current_soc

        for i in range(n):
            solar_available = pv_forecast[i]
            load_demand = load_forecast[i]

            # 光伏 -> 负载
            solar_to_load[i] = min(solar_available, load_demand)
            remaining_solar = solar_available - solar_to_load[i]
            remaining_load = load_demand - solar_to_load[i]

            # 光伏 -> 电池（优先充电）
            if remaining_solar > 0:
                soc_percent = battery_soc[i]
                if soc_percent < 95:  # 充到95%
                    available_capacity = (95 - soc_percent) / 100 * self.battery.capacity_kwh
                    max_charge = min(
                        remaining_solar,
                        self.battery.max_charge_power,
                        available_capacity
                    )
                    solar_to_battery[i] = max_charge
                    remaining_solar -= max_charge

            # 多余光伏才上网
            solar_to_grid[i] = remaining_solar

            # 负载优先从电池取电
            if remaining_load > 0:
                soc_percent = battery_soc[i]
                if soc_percent > 10:  # 放到10%
                    available_energy = (soc_percent - 10) / 100 * self.battery.capacity_kwh
                    max_discharge = min(
                        remaining_load,
                        self.battery.max_discharge_power,
                        available_energy
                    )
                    battery_to_load[i] = max_discharge
                    remaining_load -= max_discharge

            # 最后才从电网购电
            grid_to_load[i] = remaining_load

            # 更新SOC
            energy_change = (
                solar_to_battery[i] * self.battery.charge_efficiency -
                battery_to_load[i] / self.battery.discharge_efficiency
            )
            battery_soc[i + 1] = battery_soc[i] + energy_change / self.battery.capacity_kwh * 100

        return EnergySchedule(
            solar_to_load=solar_to_load,
            solar_to_battery=solar_to_battery,
            solar_to_grid=solar_to_grid,
            battery_to_load=battery_to_load,
            grid_to_load=grid_to_load,
            grid_to_battery=grid_to_battery,
            battery_soc=battery_soc[:-1]
        )

    def _optimize_backup(
        self,
        pv_forecast: np.ndarray,
        load_forecast: np.ndarray,
        backup_hours: float
    ) -> EnergySchedule:
        """备用电源模式 - 保持最低备用SOC"""
        n = self.time_horizon

        # 计算备用SOC（关键负载）
        critical_load = sum(
            load.power_rating for load in self.loads
            if load.priority == LoadPriority.CRITICAL
        )
        backup_energy = critical_load * backup_hours
        min_backup_soc = backup_energy / self.battery.capacity_kwh * 100
        min_backup_soc = max(min_backup_soc, 30)  # 至少30%

        # 使用经济模式，但SOC下限调整为min_backup_soc
        schedule = self._optimize_economic(pv_forecast, load_forecast, 10.0)

        # 调整SOC下限
        for i in range(n):
            if schedule.battery_soc[i] < min_backup_soc:
                # 限制放电，保持备用SOC
                excess_discharge = min_backup_soc - schedule.battery_soc[i]
                schedule.battery_to_load[i] -= excess_discharge / 100 * self.battery.capacity_kwh
                schedule.grid_to_load[i] += excess_discharge / 100 * self.battery.capacity_kwh
                schedule.battery_soc[i] = min_backup_soc

        return schedule

    def _calculate_costs(self, schedule: EnergySchedule) -> Dict:
        """计算成本"""
        # 从电网购电成本
        grid_purchase = np.sum(schedule.grid_to_load + schedule.grid_to_battery)
        cost_from_grid = np.sum(
            (schedule.grid_to_load + schedule.grid_to_battery) * self.prices / 100
        )  # ¢ → $

        # 上网收益
        solar_export = np.sum(schedule.solar_to_grid)
        # 假设上网电价为购电电价的60%
        feed_in_tariff = self.prices * 0.6
        revenue_from_export = np.sum(schedule.solar_to_grid * feed_in_tariff / 100)

        # 无优化情况（全部从电网购电）
        total_load = np.sum(
            schedule.solar_to_load + schedule.battery_to_load + schedule.grid_to_load
        )
        baseline_cost = np.sum(
            self._generate_load_forecast() * self.prices / 100
        )

        savings = baseline_cost - cost_from_grid + revenue_from_export

        return {
            'grid_purchase_kwh': grid_purchase,
            'cost_from_grid_usd': cost_from_grid,
            'solar_export_kwh': solar_export,
            'revenue_from_export_usd': revenue_from_export,
            'net_cost_usd': cost_from_grid - revenue_from_export,
            'baseline_cost_usd': baseline_cost,
            'savings_usd': savings,
            'savings_percentage': savings / baseline_cost * 100 if baseline_cost > 0 else 0
        }

    def _calculate_performance(
        self,
        schedule: EnergySchedule,
        pv_forecast: np.ndarray,
        load_forecast: np.ndarray
    ) -> Dict:
        """计算性能指标"""
        total_pv = np.sum(pv_forecast)
        total_load = np.sum(load_forecast)

        # 自给率：由光伏+电池供电的比例
        self_consumption = np.sum(schedule.solar_to_load + schedule.battery_to_load)
        self_sufficiency = self_consumption / total_load * 100 if total_load > 0 else 0

        # 光伏自用率：光伏直接使用或存入电池的比例
        pv_self_consumed = np.sum(schedule.solar_to_load + schedule.solar_to_battery)
        pv_self_consumption_rate = pv_self_consumed / total_pv * 100 if total_pv > 0 else 0

        # 电池循环
        battery_throughput = np.sum(
            schedule.solar_to_battery + schedule.grid_to_battery +
            schedule.battery_to_load
        )
        equivalent_cycles = battery_throughput / self.battery.capacity_kwh

        return {
            'self_sufficiency_percent': self_sufficiency,
            'pv_self_consumption_percent': pv_self_consumption_rate,
            'battery_cycles': equivalent_cycles,
            'grid_dependency_percent': 100 - self_sufficiency,
            'total_pv_generation_kwh': total_pv,
            'total_load_kwh': total_load
        }

    def _schedule_loads(
        self,
        schedule: EnergySchedule,
        load_forecast: np.ndarray
    ) -> Dict:
        """负载调度计划"""
        load_schedules = {}

        for load in self.loads:
            if not load.controllable:
                load_schedules[load.name] = {
                    'scheduled': False,
                    'reason': 'Not controllable'
                }
                continue

            # 找到最佳时段（低电价 + 光伏充足）
            best_hours = []
            for i in range(self.time_horizon):
                # 判断是否在时间窗口内
                if load.time_window:
                    if not (load.time_window[0] <= i <= load.time_window[1]):
                        continue

                # 优先选择光伏充足且电价低的时段
                if schedule.solar_to_battery[i] > 0 or self.prices[i] < np.median(self.prices):
                    best_hours.append(i)

            load_schedules[load.name] = {
                'scheduled': True,
                'best_hours': best_hours[:5],  # 前5个最佳时段
                'priority': load.priority.name,
                'power_kw': load.power_rating
            }

        return load_schedules

    def _generate_recommendations(
        self,
        schedule: EnergySchedule,
        performance: Dict
    ) -> Dict:
        """生成优化建议"""
        avg_soc = np.mean(schedule.battery_soc)

        recommendations = {
            'battery_management': [],
            'load_management': [],
            'system_upgrade': []
        }

        # 电池管理建议
        if avg_soc < 40:
            recommendations['battery_management'].append(
                '建议增加谷电时段充电，提高平均SOC'
            )
        elif avg_soc > 80:
            recommendations['battery_management'].append(
                '电池SOC偏高，可增加峰电时段放电以获得收益'
            )

        # 自给率建议
        if performance['self_sufficiency_percent'] < 60:
            recommendations['system_upgrade'].append(
                '自给率较低，建议增加光伏装机容量或电池容量'
            )

        # 负载管理建议
        controllable_loads = [load for load in self.loads if load.controllable]
        if len(controllable_loads) > 0:
            recommendations['load_management'].append(
                f'有{len(controllable_loads)}个可控负载，建议在低电价时段运行'
            )

        return recommendations


def main():
    """主函数 - 示例用法"""
    # 创建光伏系统
    solar = SolarGeneration(
        capacity_kw=8.0,
        efficiency=0.20
    )

    # 创建储能系统
    battery = BatteryStorage(
        capacity_kwh=13.5,
        current_soc=45.0,
        max_charge_power=5.0,
        max_discharge_power=5.0
    )

    # 创建家庭负载
    loads = [
        HouseholdLoad(
            name='照明',
            power_rating=0.3,
            controllable=False,
            priority=LoadPriority.HIGH
        ),
        HouseholdLoad(
            name='空调',
            power_rating=2.5,
            controllable=True,
            priority=LoadPriority.MEDIUM,
            time_window=(8, 20)
        ),
        HouseholdLoad(
            name='电动车',
            power_rating=7.0,
            controllable=True,
            priority=LoadPriority.LOW,
            time_window=(18, 7)  # 18:00-次日7:00
        ),
        HouseholdLoad(
            name='冰箱',
            power_rating=0.2,
            controllable=False,
            priority=LoadPriority.CRITICAL
        )
    ]

    # 电价计划（典型TOU电价）
    price_schedule = [
        8, 8, 8, 8, 8, 8, 12, 15, 20, 22, 24, 24,  # 0-11点
        22, 20, 18, 20, 22, 24, 24, 20, 15, 12, 8, 8  # 12-23点
    ]  # ¢/kWh

    # 创建优化器
    optimizer = HomeEnergyOptimizer(solar, battery, loads, price_schedule)

    # 执行优化
    result = optimizer.optimize(mode='economic')

    # 输出结果
    print("=" * 60)
    print("家庭储能优化结果")
    print("=" * 60)

    print("\n成本分析:")
    for key, value in result.cost_analysis.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    print("\n性能指标:")
    for key, value in result.performance_metrics.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    print("\n负载调度:")
    for load_name, schedule in result.load_schedule.items():
        print(f"  {load_name}: {schedule}")

    print("\n优化建议:")
    for category, suggestions in result.recommendations.items():
        print(f"  {category}:")
        for suggestion in suggestions:
            print(f"    - {suggestion}")


if __name__ == '__main__':
    main()
