"""
I5.4 虚拟电站VPP系统 - 核心算法实现

虚拟电厂聚合管理，将分布式储能、可控负荷、分布式电源等聚合参与电力市场。
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class VPPResource:
    """VPP资源"""
    resource_id: str
    resource_type: str  # storage/load/dg
    capacity_kw: float
    capacity_kwh: float
    location: tuple
    response_time_s: float
    availability: float


@dataclass
class VPPBid:
    """VPP竞价"""
    quantity_kw: float
    price_yuan_per_kw: float
    time_window: tuple


class VirtualPowerPlant:
    """虚拟电站管理器"""

    def __init__(self, config: Dict):
        self.config = config
        self.resources: List[VPPResource] = []

    def aggregate_resources(self, resource_list: List[Dict]) -> Dict:
        """
        聚合分布式资源

        Args:
            resource_list: 资源列表

        Returns:
            聚合结果
        """
        total_capacity_kw = 0
        total_capacity_kwh = 0
        total_energy_kwh = 0

        for res_dict in resource_list:
            resource = VPPResource(**res_dict)
            self.resources.append(resource)

            total_capacity_kw += resource.capacity_kw
            total_capacity_kwh += resource.capacity_kwh
            total_energy_kwh += resource.capacity_kwh * resource.availability

        return {
            'total_capacity_kw': total_capacity_kw,
            'total_capacity_kwh': total_capacity_kwh,
            'available_energy_kwh': total_energy_kwh,
            'resource_count': len(self.resources),
            'aggregation_time': datetime.now().isoformat()
        }

    def generate_bid(self, market_type: str, horizon_hours: int = 24) -> VPPBid:
        """
        生成市场竞价

        Args:
            market_type: 市场类型 (frequency_regulation/day_ahead/real_time)
            horizon_hours: 竞价时长

        Returns:
            竞价结果
        """
        # 计算可调节能力
        available_power = sum(r.capacity_kw * r.availability for r in self.resources)

        # 根据市场类型设定价格
        if market_type == 'frequency_regulation':
            price = 80  # 元/kW/月
        elif market_type == 'day_ahead':
            price = 0.8  # 元/kWh
        else:
            price = 1.0  # 元/kWh

        return VPPBid(
            quantity_kw=available_power,
            price_yuan_per_kw=price,
            time_window=(datetime.now(), datetime.now() + pd.Timedelta(hours=horizon_hours))
        )

    def dispatch(self, target_power_kw: float) -> Dict:
        """
        下发调度指令

        Args:
            target_power_kw: 目标出力

        Returns:
            调度结果
        """
        total_capacity = sum(r.capacity_kw for r in self.resources)
        dispatch_commands = []

        for resource in self.resources:
            # 按容量比例分配
            allocated_power = target_power_kw * (resource.capacity_kw / total_capacity)
            dispatch_commands.append({
                'resource_id': resource.resource_id,
                'target_power_kw': allocated_power,
                'response_time_s': resource.response_time_s
            })

        return {
            'dispatch_time': datetime.now().isoformat(),
            'total_target_power_kw': target_power_kw,
            'commands': dispatch_commands,
            'status': 'dispatched'
        }


def main():
    """演示"""
    print("I5.4 虚拟电站VPP系统")

    vpp = VirtualPowerPlant({})

    # 模拟资源
    resources = [
        {
            'resource_id': 'ESS_001',
            'resource_type': 'storage',
            'capacity_kw': 500,
            'capacity_kwh': 1000,
            'location': (31.23, 121.47),
            'response_time_s': 1.0,
            'availability': 0.95
        },
        {
            'resource_id': 'ESS_002',
            'resource_type': 'storage',
            'capacity_kw': 300,
            'capacity_kwh': 600,
            'location': (31.24, 121.48),
            'response_time_s': 1.5,
            'availability': 0.90
        }
    ]

    # 聚合资源
    aggregation = vpp.aggregate_resources(resources)
    print(f"\n聚合结果:")
    print(f"  总功率: {aggregation['total_capacity_kw']} kW")
    print(f"  总容量: {aggregation['total_capacity_kwh']} kWh")
    print(f"  资源数: {aggregation['resource_count']}")

    # 生成竞价
    bid = vpp.generate_bid('frequency_regulation')
    print(f"\n竞价结果:")
    print(f"  出力: {bid.quantity_kw} kW")
    print(f"  价格: {bid.price_yuan_per_kw} 元/kW")

    # 下发调度
    dispatch = vpp.dispatch(target_power_kw=400)
    print(f"\n调度指令:")
    for cmd in dispatch['commands']:
        print(f"  {cmd['resource_id']}: {cmd['target_power_kw']:.1f} kW")


if __name__ == "__main__":
    main()
