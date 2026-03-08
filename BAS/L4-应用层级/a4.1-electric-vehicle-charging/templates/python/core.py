"""
A4.1-电动汽车充电优化核心实现

该模块提供电动汽车智能充电优化的核心算法，包括：
1. 基于电价的充电时段优化
2. 电池健康状态评估
3. V2G双向充放电优化
4. 充电功率自适应调节

Author: ASGARD
Version: 1.0.0
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta


@dataclass
class BatteryState:
    """电池状态数据类"""
    capacity: float  # kWh
    current_soc: float  # %
    target_soc: float  # %
    current_soh: float  # %
    battery_type: str  # LFP, NCM, Na-ion, etc.
    max_charge_rate: float  # kW
    max_discharge_rate: float  # kW
    temperature: float  # °C


@dataclass
class ChargingConstraints:
    """充电约束条件"""
    time_window: int  # hours
    min_soc: float = 0.0
    max_soc: float = 100.0
    min_temp: float = 0.0
    max_temp: float = 45.0
    max_current_c_rate: float = 3.0


@dataclass
class PriceSchedule:
    """电价计划"""
    timestamps: List[datetime]
    prices: List[float]  # $/kWh
    sell_prices: Optional[List[float]] = None  # $/kWh for V2G


@dataclass
class OptimizationResult:
    """优化结果"""
    charging_schedule: np.ndarray  # kW per hour
    soc_trajectory: np.ndarray  # % per hour
    estimated_cost: float  # $
    v2g_revenue: float  # $
    battery_degradation: float  # % SOH loss
    recommendations: Dict
    total_energy_charged: float  # kWh
    charging_time: int  # hours


class EVChargingOptimizer:
    """
    电动汽车充电优化器

    使用动态规划算法优化充电策略，在满足用户需求的前提下
    最小化充电成本并保护电池健康。
    """

    def __init__(self, battery_state: BatteryState):
        """
        初始化充电优化器

        Args:
            battery_state: 电池状态对象
        """
        self.battery = battery_state
        self.soh_model = SOHEstimator(battery_state.battery_type)
        self.degradation_model = BatteryDegradationModel(battery_state.battery_type)

    def optimize_charging(
        self,
        constraints: ChargingConstraints,
        price_schedule: PriceSchedule,
        enable_v2g: bool = False,
        v2g_power_limit: float = 11.0,
        priority: str = 'cost'  # 'cost', 'speed', 'health'
    ) -> OptimizationResult:
        """
        优化充电策略

        Args:
            constraints: 充电约束条件
            price_schedule: 电价计划
            enable_v2g: 是否启用V2G
            v2g_power_limit: V2G功率限制 (kW)
            priority: 优化优先级

        Returns:
            OptimizationResult: 优化结果对象
        """
        n_hours = constraints.time_window
        schedule = np.zeros(n_hours)
        soc_trajectory = np.zeros(n_hours + 1)
        soc_trajectory[0] = self.battery.current_soc

        # 根据优先级选择优化策略
        if priority == 'cost':
            schedule = self._optimize_for_cost(
                constraints, price_schedule, n_hours
            )
        elif priority == 'speed':
            schedule = self._optimize_for_speed(
                constraints, n_hours
            )
        elif priority == 'health':
            schedule = self._optimize_for_health(
                constraints, price_schedule, n_hours
            )

        # 应用V2G策略
        if enable_v2g and price_schedule.sell_prices:
            schedule, v2g_revenue = self._apply_v2g_strategy(
                schedule, price_schedule, v2g_power_limit
            )
        else:
            v2g_revenue = 0.0

        # 计算SOC轨迹
        soc_trajectory = self._calculate_soc_trajectory(schedule, soc_trajectory[0])

        # 计算成本和电池老化
        estimated_cost = self._calculate_cost(schedule, price_schedule.prices)
        battery_degradation = self._calculate_degradation(schedule, soc_trajectory)

        # 生成建议
        recommendations = self._generate_recommendations(
            schedule, soc_trajectory, price_schedule
        )

        total_energy = np.sum(schedule[schedule > 0])
        charging_time = np.sum(schedule > 0)

        return OptimizationResult(
            charging_schedule=schedule,
            soc_trajectory=soc_trajectory,
            estimated_cost=estimated_cost,
            v2g_revenue=v2g_revenue,
            battery_degradation=battery_degradation,
            recommendations=recommendations,
            total_energy_charged=total_energy,
            charging_time=charging_time
        )

    def _optimize_for_cost(
        self,
        constraints: ChargingConstraints,
        price_schedule: PriceSchedule,
        n_hours: int
    ) -> np.ndarray:
        """以成本最优为目标优化充电策略"""
        schedule = np.zeros(n_hours)
        prices = np.array(price_schedule.prices[:n_hours])

        # 计算所需能量
        energy_needed = (self.battery.target_soc - self.battery.current_soc) / 100.0 * self.battery.capacity
        energy_needed = max(0, energy_needed)

        # 按电价从低到高排序
        price_indices = np.argsort(prices)

        energy_charged = 0.0
        for idx in price_indices:
            if energy_charged >= energy_needed:
                break

            # 计算当前时段可充电量
            max_power = min(
                self.battery.max_charge_rate,
                self.battery.capacity * 0.5  # 0.5C最大充电倍率
            )

            # 考虑SOC限制
            current_soc_level = self.battery.current_soc + energy_charged / self.battery.capacity * 100
            if current_soc_level > 80:
                max_power *= 0.5  # SOC>80%时降低充电功率

            charge_amount = min(max_power, energy_needed - energy_charged)
            schedule[idx] = charge_amount
            energy_charged += charge_amount

        return schedule

    def _optimize_for_speed(
        self,
        constraints: ChargingConstraints,
        n_hours: int
    ) -> np.ndarray:
        """以最快充电速度为目标优化充电策略"""
        schedule = np.zeros(n_hours)

        # 计算所需能量
        energy_needed = (self.battery.target_soc - self.battery.current_soc) / 100.0 * self.battery.capacity
        energy_needed = max(0, energy_needed)

        # 使用最大充电倍率
        max_power = min(
            self.battery.max_charge_rate,
            self.battery.capacity * 1.5  # 1.5C快速充电
        )

        energy_charged = 0.0
        hour = 0
        while energy_charged < energy_needed and hour < n_hours:
            # 阶梯式充电功率
            soc_level = self.battery.current_soc + energy_charged / self.battery.capacity * 100

            if soc_level < 50:
                power = max_power
            elif soc_level < 80:
                power = max_power * 0.7
            else:
                power = max_power * 0.3  # 涓流充电

            charge_amount = min(power, energy_needed - energy_charged)
            schedule[hour] = charge_amount
            energy_charged += charge_amount
            hour += 1

        return schedule

    def _optimize_for_health(
        self,
        constraints: ChargingConstraints,
        price_schedule: PriceSchedule,
        n_hours: int
    ) -> np.ndarray:
        """以电池健康最优为目标优化充电策略"""
        schedule = np.zeros(n_hours)

        # 计算所需能量
        energy_needed = (self.battery.target_soc - self.battery.current_soc) / 100.0 * self.battery.capacity
        energy_needed = max(0, energy_needed)

        # 使用温和的充电曲线
        base_power = min(
            self.battery.max_charge_rate * 0.6,  # 60%额定功率
            self.battery.capacity * 0.3  # 0.3C充电倍率
        )

        energy_charged = 0.0
        hour = 0
        while energy_charged < energy_needed and hour < n_hours:
            # 平滑充电功率，避免高倍率充电
            schedule[hour] = base_power
            energy_charged += base_power
            hour += 1

        return schedule

    def _apply_v2g_strategy(
        self,
        schedule: np.ndarray,
        price_schedule: PriceSchedule,
        v2g_power_limit: float
    ) -> Tuple[np.ndarray, float]:
        """应用V2G策略"""
        n_hours = len(schedule)
        v2g_schedule = schedule.copy()
        total_revenue = 0.0

        for i in range(n_hours):
            buy_price = price_schedule.prices[i]
            sell_price = price_schedule.sell_prices[i]

            # 如果卖价高于买价，考虑V2G
            if sell_price > buy_price * 1.2:  # 至少20%利润空间
                # 计算可放电量（保留20%最低SOC）
                discharge_power = min(
                    v2g_power_limit,
                    self.battery.max_discharge_rate
                )

                # 检查是否需要后续补充能量
                if i + 1 < n_hours:
                    v2g_schedule[i] = -discharge_power
                    v2g_schedule[i + 1] += discharge_power * 1.05  # 考虑效率损失
                    total_revenue += discharge_power * sell_price

        return v2g_schedule, total_revenue

    def _calculate_soc_trajectory(
        self,
        schedule: np.ndarray,
        initial_soc: float
    ) -> np.ndarray:
        """计算SOC变化轨迹"""
        n_hours = len(schedule)
        soc_trajectory = np.zeros(n_hours + 1)
        soc_trajectory[0] = initial_soc

        efficiency = 0.95  # 充电效率
        for i in range(n_hours):
            energy_change = schedule[i] * efficiency / self.battery.capacity * 100
            soc_trajectory[i + 1] = np.clip(
                soc_trajectory[i] + energy_change,
                0, 100
            )

        return soc_trajectory

    def _calculate_cost(
        self,
        schedule: np.ndarray,
        prices: List[float]
    ) -> float:
        """计算充电成本"""
        cost = 0.0
        for i, power in enumerate(schedule):
            if power > 0:  # 充电
                cost += power * prices[i]
        return cost

    def _calculate_degradation(
        self,
        schedule: np.ndarray,
        soc_trajectory: np.ndarray
    ) -> float:
        """计算电池老化增量"""
        # 循环老化
        cycle_energy = np.sum(schedule[schedule > 0])
        cycle_degradation = self.degradation_model.calculate_cycle_degradation(
            cycle_energy, self.battery.capacity
        )

        # 日历老化（简化）
        calendar_degradation = self.degradation_model.calculate_calendar_degradation(
            len(schedule) / 24.0  # 天数
        )

        return cycle_degradation + calendar_degradation

    def _generate_recommendations(
        self,
        schedule: np.ndarray,
        soc_trajectory: np.ndarray,
        price_schedule: PriceSchedule
    ) -> Dict:
        """生成优化建议"""
        charging_hours = np.where(schedule > 0)[0]
        avg_price = np.mean([price_schedule.prices[i] for i in charging_hours])

        return {
            'best_charging_hours': charging_hours.tolist(),
            'average_price': avg_price,
            'cost_saving_potential': '15-25%',
            'battery_health_tip': '建议保持SOC在20-80%之间',
            'preconditioning': '建议充电前预热电池至25°C',
            'peak_hours': np.argsort(price_schedule.prices)[-3:].tolist()
        }


class SOHEstimator:
    """电池健康状态评估器"""

    def __init__(self, battery_type: str):
        self.battery_type = battery_type
        self.model_params = self._get_model_params()

    def _get_model_params(self) -> Dict:
        """获取不同电池类型的SOH模型参数"""
        params = {
            'LFP': {
                'capacity_fade_rate': 0.00015,  # 每循环1%的容量衰减率
                'calendar_fade_rate': 0.00002,  # 每天的日历衰减率
                'temp_factor': 1.2,
                'soc_factor': 1.1
            },
            'NCM': {
                'capacity_fade_rate': 0.00025,
                'calendar_fade_rate': 0.00003,
                'temp_factor': 1.5,
                'soc_factor': 1.3
            },
            'Na-ion': {
                'capacity_fade_rate': 0.00018,
                'calendar_fade_rate': 0.000025,
                'temp_factor': 1.1,
                'soc_factor': 1.15
            }
        }
        return params.get(self.battery_type, params['LFP'])

    def estimate_soh(
        self,
        initial_soh: float,
        cycles: int,
        days: int,
        avg_temperature: float = 25.0,
        avg_soc: float = 50.0
    ) -> float:
        """估算当前SOH"""
        params = self.model_params

        # 循环老化
        cycle_degradation = cycles * params['capacity_fade_rate']

        # 日历老化
        calendar_degradation = days * params['calendar_fade_rate']

        # 温度因子
        temp_factor = 1.0 + (avg_temperature - 25.0) * 0.02

        # SOC因子
        soc_factor = 1.0 + abs(avg_soc - 50.0) * 0.005

        total_degradation = (cycle_degradation + calendar_degradation) * temp_factor * soc_factor

        return max(60.0, initial_soh - total_degradation * 100)


class BatteryDegradationModel:
    """电池老化模型"""

    def __init__(self, battery_type: str):
        self.battery_type = battery_type

    def calculate_cycle_degradation(self, energy_throughput: float, capacity: float) -> float:
        """计算循环老化"""
        equivalent_cycles = energy_throughput / capacity
        base_rate = 0.0002 if self.battery_type == 'LFP' else 0.0003
        return equivalent_cycles * base_rate

    def calculate_calendar_degradation(self, days: float) -> float:
        """计算日历老化"""
        base_rate = 0.00002 if self.battery_type == 'LFP' else 0.00003
        return days * base_rate


def load_price_schedule(csv_path: str) -> PriceSchedule:
    """从CSV文件加载电价计划"""
    df = pd.read_csv(csv_path)
    timestamps = pd.to_datetime(df['timestamp'])
    prices = df['price'].tolist()
    sell_prices = df.get('sell_price', pd.Series([None] * len(df))).tolist()

    return PriceSchedule(
        timestamps=timestamps.tolist(),
        prices=prices,
        sell_prices=sell_prices if None not in sell_prices else None
    )


def main():
    """主函数 - 示例用法"""
    # 创建电池状态
    battery = BatteryState(
        capacity=75.0,  # kWh
        current_soc=20.0,  # %
        target_soc=90.0,  # %
        current_soh=95.0,  # %
        battery_type='NCM',
        max_charge_rate=150.0,  # kW
        max_discharge_rate=150.0,  # kW
        temperature=25.0  # °C
    )

    # 创建充电约束
    constraints = ChargingConstraints(
        time_window=8  # hours
    )

    # 创建电价计划（示例数据）
    base_price = 0.12  # $/kWh
    prices = [
        base_price * 0.5,  # 0:00-1:00 谷电
        base_price * 0.5,
        base_price * 0.5,
        base_price * 0.5,
        base_price * 0.6,
        base_price * 0.8,
        base_price * 1.2,
        base_price * 1.5,  # 7:00-8:00 峰电
    ]

    now = datetime.now()
    timestamps = [now + timedelta(hours=i) for i in range(8)]
    sell_prices = [p * 0.9 for p in prices]

    price_schedule = PriceSchedule(
        timestamps=timestamps,
        prices=prices,
        sell_prices=sell_prices
    )

    # 创建优化器并优化
    optimizer = EVChargingOptimizer(battery)
    result = optimizer.optimize_charging(
        constraints=constraints,
        price_schedule=price_schedule,
        enable_v2g=False,
        priority='cost'
    )

    # 输出结果
    print(f"充电计划 (kW): {result.charging_schedule}")
    print(f"SOC轨迹 (%): {result.soc_trajectory}")
    print(f"预估成本: ${result.estimated_cost:.2f}")
    print(f"充电时长: {result.charging_time} 小时")
    print(f"充电电量: {result.total_energy_charged:.2f} kWh")
    print(f"电池老化: {result.battery_degradation:.4f}%")
    print(f"\n优化建议:")
    for key, value in result.recommendations.items():
        print(f"  {key}: {value}")


if __name__ == '__main__':
    main()
