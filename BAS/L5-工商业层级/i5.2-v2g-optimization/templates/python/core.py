"""
I5.2 V2G双向优化系统 - 核心算法实现

Vehicle-to-Grid (V2G) 双向充放电优化，协调车辆出行需求与电网辅助服务。
支持调频、峰谷套利、备用容量等多种V2G服务模式。

主要功能：
1. 车辆出行模式预测
2. V2G充放电优化（MILP）
3. 电池寿命衰减评估
4. 收益计算与结算
5. 实时控制指令生成
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy.optimize import linprog


@dataclass
class VehicleConfig:
    """车辆配置"""
    battery_capacity_kwh: float
    max_charge_power_kw: float
    max_discharge_power_kw: float
    max_v2g_power_kw: float
    soc_min: float
    soc_max: float
    charge_efficiency: float
    discharge_efficiency: float
    battery_type: str
    cycle_life_80dod: int
    battery_cost_yuan_kwh: float


@dataclass
class MobilityPattern:
    """出行模式"""
    work_start_hour: int
    work_end_hour: int
    home_charging_hours: List[int]
    average_daily_distance_km: float
    minimum_trip_soc: float


@dataclass
class V2GServiceConfig:
    """V2G服务配置"""
    frequency_regulation_price: float
    peak_price: float
    valley_price: float
    reserve_capacity_price: float
    peak_hours: List[int]
    valley_hours: List[int]


@dataclass
class V2GSchedule:
    """V2G调度计划"""
    timestamp: List[datetime]
    soc: np.ndarray
    p_charge: np.ndarray
    p_discharge: np.ndarray
    p_v2g: np.ndarray
    service_type: List[str]
    revenue: float
    degradation_cost: float
    net_profit: float
    v2g_energy: float


class BatteryDegradationModel:
    """电池衰减模型"""

    def __init__(self, battery_config: VehicleConfig):
        self.config = battery_config

    def calculate_degradation_cost(self, throughput_kwh: float,
                                   average_dod: float = 0.5) -> float:
        """
        计算电池衰减成本

        Args:
            throughput_kwh: 充放电吞吐量
            average_dod: 平均放电深度

        Returns:
            衰减成本 (元)
        """
        # 参考循环寿命 (80% DOD)
        ref_cycle_life = self.config.cycle_life_80dod

        # DOD影响系数 (雨流计数法简化)
        dod_factor = (average_dod / 0.8) ** 1.5

        # 实际循环寿命
        actual_cycle_life = ref_cycle_life / dod_factor

        # 等效满充满放循环次数
        equivalent_cycles = throughput_kwh / self.config.battery_capacity_kwh

        # 容量损失 (假设20%衰减为寿命终点)
        capacity_loss = (equivalent_cycles / actual_cycle_life) * 0.2

        # 电池价值损失
        degradation_cost = (capacity_loss * self.config.battery_capacity_kwh *
                          self.config.battery_cost_yuan_kwh)

        return degradation_cost


class MobilityPredictor:
    """出行预测器"""

    def __init__(self, pattern: MobilityPattern):
        self.pattern = pattern

    def predict_next_departure(self, current_time: datetime) -> datetime:
        """预测下次出发时间"""
        hour = current_time.hour

        # 如果当前时间在工作时间之前，预测上班出发
        if hour < self.pattern.work_start_hour:
            return current_time.replace(
                hour=self.pattern.work_start_hour,
                minute=0,
                second=0
            )

        # 如果在工作时间，预测下班出发
        elif hour < self.pattern.work_end_hour:
            return current_time.replace(
                hour=self.pattern.work_end_hour,
                minute=0,
                second=0
            )

        # 否则预测次日上班
        else:
            next_day = current_time + timedelta(days=1)
            return next_day.replace(
                hour=self.pattern.work_start_hour,
                minute=0,
                second=0
            )

    def estimate_trip_energy(self, distance_km: float,
                            temperature: float = 25) -> float:
        """
        估算行程能耗

        Args:
            distance_km: 行驶距离
            temperature: 环境温度 (°C)

        Returns:
            能耗 (kWh)
        """
        # 基础能耗 (kWh/km)
        base_consumption = 0.15

        # 温度修正系数
        temp_factor = 1 + 0.005 * (20 - temperature) ** 2 / 100

        energy = distance_km * base_consumption * temp_factor

        return energy


class V2GOptimizer:
    """V2G优化器"""

    def __init__(self,
                 vehicle_config: VehicleConfig,
                 mobility_pattern: MobilityPattern,
                 v2g_config: V2GServiceConfig):
        self.vehicle = vehicle_config
        self.mobility = mobility_pattern
        self.v2g = v2g_config

        self.degradation_model = BatteryDegradationModel(vehicle_config)
        self.mobility_predictor = MobilityPredictor(mobility_pattern)

    def get_price_at_hour(self, hour: int) -> float:
        """获取指定小时电价"""
        if hour in self.v2g.peak_hours:
            return self.v2g.peak_price
        elif hour in self.v2g.valley_hours:
            return self.v2g.valley_price
        else:
            return (self.v2g.peak_price + self.v2g.valley_price) / 2

    def optimize(self,
                current_time: datetime,
                current_soc: float,
                next_departure: datetime,
                trip_distance_km: float,
                optimization_horizon_hours: int = 24,
                dt_hours: float = 0.25) -> V2GSchedule:
        """
        V2G优化调度

        Args:
            current_time: 当前时间
            current_soc: 当前SOC
            next_departure: 下次出发时间
            trip_distance_km: 行程距离
            optimization_horizon_hours: 优化时域
            dt_hours: 时间步长

        Returns:
            V2G调度计划
        """
        T = int(optimization_horizon_hours / dt_hours)
        n_vars = 3 * T  # P_charge, P_discharge, P_v2g, SOC

        # 生成时间序列
        timestamp = [current_time + timedelta(hours=t*dt_hours) for t in range(T)]

        # 计算行程能耗需求
        trip_energy = self.mobility_predictor.estimate_trip_energy(trip_distance_km)
        trip_soc_required = min(trip_energy / self.vehicle.battery_capacity_kwh +
                               self.mobility.minimum_trip_soc, 0.95)

        # 找到出发时刻索引
        departure_idx = min(int((next_departure - current_time).total_seconds() / 3600 / dt_hours), T-1)

        # 目标函数：最大化收益
        # 收益 = 峰谷套利收益 + 调频收益 - 电池衰减成本
        c = np.zeros(3 * T)

        for t in range(T):
            hour = timestamp[t].hour
            price = self.get_price_at_hour(hour)

            # P_charge (充电成本)
            c[t*3 + 0] = price * dt_hours

            # P_discharge (放电收益)
            c[t*3 + 1] = -price * dt_hours * 0.95  # 考虑放电效率

            # P_v2g (调频收益，简化处理)
            c[t*3 + 2] = -self.v2g.frequency_regulation_price * dt_hours

        # 约束条件
        A = []
        b = []
        lb = []
        ub = []

        # 1. SOC动态约束
        for t in range(T-1):
            row = np.zeros(3 * T)
            row[t*3 + 1] = dt_hours / self.vehicle.discharge_efficiency / self.vehicle.battery_capacity_kwh
            row[t*3 + 0] = -dt_hours * self.vehicle.charge_efficiency / self.vehicle.battery_capacity_kwh
            row[t*3 + 2] = -dt_hours * 0.5 / self.vehicle.battery_capacity_kwh  # V2g假设50%用于调节
            A.append(row)
            b.append(0)

        # 2. 出发时刻SOC约束
        if departure_idx < T:
            row = np.zeros(3 * T)
            # SOC[next_departure] >= trip_soc_required
            for t in range(departure_idx):
                row[t*3 + 1] = dt_hours / self.vehicle.discharge_efficiency / self.vehicle.battery_capacity_kwh
                row[t*3 + 0] = -dt_hours * self.vehicle.charge_efficiency / self.vehicle.battery_capacity_kwh
                row[t*3 + 2] = -dt_hours * 0.5 / self.vehicle.battery_capacity_kwh
            A.append(row)
            b.append(trip_soc_required - current_soc)

        # 3. 功率上下界
        for t in range(T):
            # P_charge: [0, max_charge_power]
            lb.extend([0])
            ub.extend([self.vehicle.max_charge_power_kw])

            # P_discharge: [0, max_discharge_power]
            lb.extend([0])
            ub.extend([self.vehicle.max_discharge_power_kw])

            # P_v2g: [-max_v2g_power, max_v2g_power]
            lb.extend([-self.vehicle.max_v2g_power_kw])
            ub.extend([self.vehicle.max_v2g_power_kw])

        # 求解线性规划
        try:
            bounds = list(zip(lb, ub))
            res = linprog(c, A_eq=A, b_eq=b, bounds=bounds, method='highs')

            if not res.success:
                raise ValueError(f"优化失败: {res.message}")

            x = res.x

            # 提取结果
            p_charge = np.array([x[t*3 + 0] for t in range(T)])
            p_discharge = np.array([x[t*3 + 1] for t in range(T)])
            p_v2g = np.array([x[t*3 + 2] for t in range(T)])

            # 计算SOC轨迹
            soc = np.zeros(T)
            soc[0] = current_soc

            for t in range(T-1):
                delta_soc = ((p_charge[t] * self.vehicle.charge_efficiency -
                            p_discharge[t] / self.vehicle.discharge_efficiency -
                            abs(p_v2g[t]) * 0.5) *
                           dt_hours / self.vehicle.battery_capacity_kwh)
                soc[t+1] = np.clip(soc[t] + delta_soc,
                                  self.vehicle.soc_min,
                                  self.vehicle.soc_max)

            # 确定服务类型
            service_type = []
            for t in range(T):
                if abs(p_v2g[t]) > 1:
                    service_type.append("frequency_regulation")
                elif p_discharge[t] > 1:
                    hour = timestamp[t].hour
                    if hour in self.v2g.peak_hours:
                        service_type.append("peak_shaving")
                    else:
                        service_type.append("load_following")
                elif p_charge[t] > 1:
                    service_type.append("charging")
                else:
                    service_type.append("idle")

            # 计算收益
            revenue = 0
            v2g_energy = 0

            for t in range(T):
                hour = timestamp[t].hour
                price = self.get_price_at_hour(hour)

                # 峰谷套利收益
                revenue += p_discharge[t] * price * dt_hours * 0.95
                revenue -= p_charge[t] * price * dt_hours

                # 调频收益
                v2g_energy += abs(p_v2g[t]) * dt_hours
                revenue += abs(p_v2g[t]) * self.v2g.frequency_regulation_price * dt_hours

            # 电池衰减成本
            total_throughput = (p_charge.sum() + p_discharge.sum() +
                               abs(p_v2g).sum()) * dt_hours
            degradation_cost = self.degradation_model.calculate_degradation_cost(
                total_throughput, average_dod=0.4
            )

            net_profit = revenue - degradation_cost

            return V2GSchedule(
                timestamp=timestamp,
                soc=soc,
                p_charge=p_charge,
                p_discharge=p_discharge,
                p_v2g=p_v2g,
                service_type=service_type,
                revenue=revenue,
                degradation_cost=degradation_cost,
                net_profit=net_profit,
                v2g_energy=total_throughput
            )

        except Exception as e:
            print(f"V2G优化错误: {e}")
            return self._fallback_strategy(current_time, current_soc,
                                          next_departure, trip_distance_km,
                                          optimization_horizon_hours, dt_hours)

    def _fallback_strategy(self, current_time: datetime, current_soc: float,
                          next_departure: datetime, trip_distance_km: float,
                          horizon_hours: int, dt_hours: float) -> V2GSchedule:
        """备用策略：简单峰谷套利"""
        T = int(horizon_hours / dt_hours)
        timestamp = [current_time + timedelta(hours=t*dt_hours) for t in range(T)]

        soc = np.full(T, current_soc)
        p_charge = np.zeros(T)
        p_discharge = np.zeros(T)
        p_v2g = np.zeros(T)
        service_type = ["idle"] * T

        trip_energy = self.mobility_predictor.estimate_trip_energy(trip_distance_km)

        for t in range(T):
            hour = timestamp[t].hour
            price = self.get_price_at_hour(hour)

            # 谷时充电
            if price == self.v2g.valley_price and soc[t] < self.vehicle.soc_max:
                p_charge[t] = self.vehicle.max_charge_power_kw
                service_type[t] = "charging"

            # 峰时放电
            elif price == self.v2g.peak_price and soc[t] > self.vehicle.soc_min:
                p_discharge[t] = self.vehicle.max_discharge_power_kw
                service_type[t] = "peak_shaving"

            # 更新SOC
            if t < T - 1:
                delta_soc = ((p_charge[t] * self.vehicle.charge_efficiency -
                            p_discharge[t] / self.vehicle.discharge_efficiency) *
                           dt_hours / self.vehicle.battery_capacity_kwh)
                soc[t+1] = np.clip(soc[t] + delta_soc,
                                  self.vehicle.soc_min,
                                  self.vehicle.soc_max)

        return V2GSchedule(
            timestamp=timestamp,
            soc=soc,
            p_charge=p_charge,
            p_discharge=p_discharge,
            p_v2g=p_v2g,
            service_type=service_type,
            revenue=0,
            degradation_cost=0,
            net_profit=0,
            v2g_energy=0
        )


class V2GManager:
    """V2G管理系统主类"""

    def __init__(self, config: Dict):
        """初始化V2G管理器"""
        self.vehicle = VehicleConfig(**config['vehicle'])
        self.mobility = MobilityPattern(**config['mobility'])
        self.v2g_config = V2GServiceConfig(**config['v2g_services'])

        self.optimizer = V2GOptimizer(
            self.vehicle, self.mobility, self.v2g_config
        )

    def optimize_schedule(self,
                         current_time: str,
                         current_soc: float,
                         next_departure: str,
                         trip_distance_km: float) -> V2GSchedule:
        """优化V2G调度"""
        return self.optimizer.optimize(
            current_time=datetime.strptime(current_time, "%Y-%m-%dT%H:%M:%S"),
            current_soc=current_soc,
            next_departure=datetime.strptime(next_departure, "%Y-%m-%dT%H:%M:%S"),
            trip_distance_km=trip_distance_km
        )

    def realtime_control(self,
                        vehicle_id: str,
                        service_type: str,
                        current_soc: float,
                        grid_frequency: float = 50.0) -> Dict:
        """实时控制"""
        action = "idle"
        target_power = 0

        if service_type == "frequency_regulation":
            # 调频控制
            if grid_frequency > 50.1:
                # 频率偏高，增加充电
                action = "charge"
                target_power = min(10, (grid_frequency - 50.1) * 100)
            elif grid_frequency < 49.9:
                # 频率偏低，放电支持
                action = "discharge"
                target_power = min(10, (49.9 - grid_frequency) * 100)

        return {
            "action": action,
            "target_power": target_power,
            "current_soc": current_soc,
            "grid_frequency": grid_frequency
        }


def main():
    """主函数 - 演示V2G优化系统"""
    print("=" * 60)
    print("I5.2 V2G双向优化系统")
    print("=" * 60)

    # 配置
    config = {
        'vehicle': {
            'battery_capacity_kwh': 60,
            'max_charge_power_kw': 120,
            'max_discharge_power_kw': 60,
            'max_v2g_power_kw': 40,
            'soc_min': 0.1,
            'soc_max': 0.9,
            'charge_efficiency': 0.95,
            'discharge_efficiency': 0.95,
            'battery_type': 'NCM',
            'cycle_life_80dod': 3000,
            'battery_cost_yuan_kwh': 800
        },
        'mobility': {
            'work_start_hour': 8,
            'work_end_hour': 18,
            'home_charging_hours': [0, 1, 2, 3, 4, 5, 6, 22, 23],
            'average_daily_distance_km': 50,
            'minimum_trip_soc': 0.3
        },
        'v2g_services': {
            'frequency_regulation_price': 0.8,
            'peak_price': 1.2,
            'valley_price': 0.4,
            'reserve_capacity_price': 300,
            'peak_hours': [10, 11, 12, 13, 14, 15, 16, 17, 18],
            'valley_hours': [0, 1, 2, 3, 4, 5, 6, 22, 23]
        }
    }

    # 初始化管理器
    mgr = V2GManager(config)
    print("\n系统配置:")
    print(f"  电池容量: {config['vehicle']['battery_capacity_kwh']} kWh")
    print(f"  最大V2G功率: {config['vehicle']['max_v2g_power_kw']} kW")
    print(f"  工作时间: {config['mobility']['work_start_hour']}:00-{config['mobility']['work_end_hour']}:00")

    # 运行优化
    print("\n" + "=" * 60)
    print("运行V2G优化...")
    print("=" * 60)

    schedule = mgr.optimize_schedule(
        current_time="2025-03-08T18:00:00",
        current_soc=0.5,
        next_departure="2025-03-09T08:00:00",
        trip_distance_km=50
    )

    print("\n优化结果:")
    print(f"  预计收益: {schedule.revenue:.2f} 元")
    print(f"  电池衰减成本: {schedule.degradation_cost:.2f} 元")
    print(f"  净收益: {schedule.net_profit:.2f} 元")
    print(f"  V2G电量: {schedule.v2g_energy:.1f} kWh")

    # 显示前12小时调度
    print("\n前12小时调度计划:")
    print(f"{'时间':<16} {'SOC':<8} {'充电':<8} {'放电':<8} {'V2G':<8} {'服务':<20}")
    for i in range(48):  # 12小时 * 4 (15分钟间隔)
        print(f"{schedule.timestamp[i].strftime('%Y-%m-%d %H:%M'):<16} "
              f"{schedule.soc[i]:<8.2%} {schedule.p_charge[i]:<8.1f} "
              f"{schedule.p_discharge[i]:<8.1f} {schedule.p_v2g[i]:<8.1f} "
              f"{schedule.service_type[i]:<20}")

    # 实时控制演示
    print("\n" + "=" * 60)
    print("实时控制演示...")
    print("=" * 60)

    control = mgr.realtime_control(
        vehicle_id="EV_001",
        service_type="frequency_regulation",
        current_soc=0.65,
        grid_frequency=49.85
    )

    print(f"\n电网频率: {control['grid_frequency']} Hz")
    print(f"控制动作: {control['action']}")
    print(f"目标功率: {control['target_power']} kW")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
