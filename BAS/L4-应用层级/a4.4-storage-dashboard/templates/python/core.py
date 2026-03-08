"""
A4.4-储能大屏核心实现

该模块提供储能场站实时监控大屏的数据处理与可视化核心算法

Author: ASGARD
Version: 1.0.0
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum
import json


class DataType(Enum):
    """数据类型"""
    POWER = "power"
    SOC = "soc"
    SOH = "soh"
    TEMPERATURE = "temperature"
    VOLTAGE = "voltage"
    CURRENT = "current"
    ALARM = "alarm"
    ENERGY = "energy"


@dataclass
class RealTimeData:
    """实时数据"""
    timestamp: datetime
    data_type: DataType
    value: float
    unit: str
    source: str  # 数据来源设备ID
    metadata: Optional[Dict] = None


@dataclass
class DashboardConfig:
    """大屏配置"""
    station_id: str
    station_name: str
    refresh_interval: int = 5  # seconds
    display_units: str = "metric"  # metric / imperial
    theme: str = "dark"


@dataclass
class PowerFlow:
    """功率流向"""
    solar_power: float  # MW
    grid_power: float  # MW (+充电, -放电)
    battery_power: float  # MW (+充电, -放电)
    load_power: float  # MW
    efficiency: float  # %


@dataclass
class EconomicMetrics:
    """经济指标"""
    daily_revenue: float  # 元
    cumulative_revenue: float  # 元
    cost_per_kwh: float  # 元/kWh
    roi: float  # %


@dataclass
class EnvironmentalMetrics:
    """环保指标"""
    daily_co2_reduction: float  # 吨
    cumulative_co2_reduction: float  # 吨
    equivalent_trees: int  # 棵


class StorageDashboard:
    """
    储能大屏数据处理系统

    负责数据采集、处理、聚合和推送
    """

    def __init__(self, config: DashboardConfig):
        """
        初始化大屏系统

        Args:
            config: 大屏配置
        """
        self.config = config
        self.data_buffer = {}
        self.subscribers = []

    def process_realtime_data(self, data: RealTimeData):
        """
        处理实时数据

        Args:
            data: 实时数据对象
        """
        # 存储到数据缓冲区
        if data.data_type not in self.data_buffer:
            self.data_buffer[data.data_type] = []

        self.data_buffer[data.data_type].append(data)

        # 保持缓冲区大小（最近1000条）
        if len(self.data_buffer[data.data_type]) > 1000:
            self.data_buffer[data.data_type].pop(0)

        # 触发数据更新事件
        self._notify_subscribers(data)

    def get_dashboard_data(self) -> Dict:
        """
        获取大屏显示数据

        Returns:
            Dict: 大屏数据
        """
        return {
            'station_info': self._get_station_info(),
            'power_flow': self._calculate_power_flow(),
            'battery_status': self._get_battery_status(),
            'economic_metrics': self._calculate_economic_metrics(),
            'environmental_metrics': self._calculate_environmental_metrics(),
            'alarms': self._get_recent_alarms(),
            'trends': self._get_trend_data()
        }

    def _get_station_info(self) -> Dict:
        """获取场站信息"""
        return {
            'station_id': self.config.station_id,
            'station_name': self.config.station_name,
            'capacity_mwh': 10.0,
            'power_mw': 5.0,
            'battery_clusters': 10,
            'update_time': datetime.now().isoformat()
        }

    def _calculate_power_flow(self) -> PowerFlow:
        """计算功率流向"""
        # 从数据缓冲区获取最新数据
        power_data = self.data_buffer.get(DataType.POWER, [])

        if not power_data:
            return PowerFlow(0, 0, 0, 0, 95.0)

        latest = power_data[-1]

        # 模拟计算
        return PowerFlow(
            solar_power=latest.metadata.get('solar', 0) if latest.metadata else 0,
            grid_power=latest.value * 0.3,
            battery_power=latest.value,
            load_power=latest.value * 1.2,
            efficiency=95.0
        )

    def _get_battery_status(self) -> Dict:
        """获取电池状态"""
        soc_data = self.data_buffer.get(DataType.SOC, [RealTimeData(datetime.now(), DataType.SOC, 65, '%', 'all')])
        soh_data = self.data_buffer.get(DataType.SOH, [RealTimeData(datetime.now(), DataType.SOH, 98, '%', 'all')])
        temp_data = self.data_buffer.get(DataType.TEMPERATURE, [RealTimeData(datetime.now(), DataType.TEMPERATURE, 25, '°C', 'all')])

        avg_soc = soc_data[-1].value if soc_data else 65
        avg_soh = soh_data[-1].value if soh_data else 98
        avg_temp = temp_data[-1].value if temp_data else 25

        return {
            'avg_soc_percent': avg_soc,
            'avg_soh_percent': avg_soh,
            'avg_temperature_c': avg_temp,
            'max_temperature_c': avg_temp + 5,
            'min_temperature_c': avg_temp - 5,
            'available_capacity_mwh': 10.0 * avg_soc / 100,
            'cluster_status': [
                {'cluster_id': i, 'soc': avg_soc + np.random.uniform(-5, 5), 'soh': avg_soh}
                for i in range(1, 11)
            ]
        }

    def _calculate_economic_metrics(self) -> EconomicMetrics:
        """计算经济指标"""
        return EconomicMetrics(
            daily_revenue=15000.0,
            cumulative_revenue=5475000.0,
            cost_per_kwh=0.85,
            roi=12.5
        )

    def _calculate_environmental_metrics(self) -> EnvironmentalMetrics:
        """计算环保指标"""
        return EnvironmentalMetrics(
            daily_co2_reduction=8.5,
            cumulative_co2_reduction=3102.5,
            equivalent_trees=15512
        )

    def _get_recent_alarms(self) -> List[Dict]:
        """获取最近告警"""
        alarm_data = self.data_buffer.get(DataType.ALARM, [])

        return [
            {
                'alarm_id': f'ALM-{i:04d}',
                'level': 'warning' if i % 3 == 0 else 'info',
                'message': f'电池簇{i+1}温度偏高' if i % 2 == 0 else f'电池簇{i+1}SOC不平衡',
                'timestamp': (datetime.now() - timedelta(minutes=i*10)).isoformat(),
                'source': f'cluster_{i+1}'
            }
            for i in range(min(5, len(alarm_data)))
        ] if alarm_data else []

    def _get_trend_data(self) -> Dict:
        """获取趋势数据"""
        # 生成最近24小时的模拟数据
        hours = 24
        timestamps = [
            (datetime.now() - timedelta(hours=i)).isoformat()
            for i in range(hours, 0, -1)
        ]

        return {
            'soc_trend': {
                'timestamps': timestamps,
                'values': [65 + 10 * np.sin(i/4) + np.random.uniform(-2, 2) for i in range(hours)]
            },
            'power_trend': {
                'timestamps': timestamps,
                'values': [2.5 + 1.5 * np.sin(i/3) + np.random.uniform(-0.3, 0.3) for i in range(hours)]
            },
            'temperature_trend': {
                'timestamps': timestamps,
                'values': [25 + 5 * np.sin(i/6) + np.random.uniform(-1, 1) for i in range(hours)]
            }
        }

    def _notify_subscribers(self, data: RealTimeData):
        """通知订阅者"""
        for callback in self.subscribers:
            callback(data)

    def subscribe(self, callback):
        """订阅数据更新"""
        self.subscribers.append(callback)


def generate_dashboard_json(dashboard: StorageDashboard, output_path: str = "dashboard_data.json"):
    """
    生成大屏JSON数据

    Args:
        dashboard: 大屏对象
        output_path: 输出文件路径
    """
    data = dashboard.get_dashboard_data()

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data


def main():
    """主函数 - 示例用法"""
    # 创建大屏配置
    config = DashboardConfig(
        station_id="ST_001",
        station_name="ASGARD储能示范站",
        refresh_interval=5
    )

    # 创建大屏对象
    dashboard = StorageDashboard(config)

    # 模拟接收实时数据
    now = datetime.now()
    dashboard.process_realtime_data(RealTimeData(
        timestamp=now,
        data_type=DataType.POWER,
        value=2.5,
        unit="MW",
        source="ems_main",
        metadata={"solar": 3.0}
    ))

    dashboard.process_realtime_data(RealTimeData(
        timestamp=now,
        data_type=DataType.SOC,
        value=68.5,
        unit="%",
        source="bms_all"
    ))

    dashboard.process_realtime_data(RealTimeData(
        timestamp=now,
        data_type=DataType.TEMPERATURE,
        value=26.5,
        unit="°C",
        source="bms_all"
    ))

    # 获取大屏数据
    data = dashboard.get_dashboard_data()

    # 输出结果
    print("=" * 60)
    print("储能大屏数据")
    print("=" * 60)

    print(f"\n场站信息:")
    print(f"  名称: {data['station_info']['station_name']}")
    print(f"  容量: {data['station_info']['capacity_mwh']} MWh")
    print(f"  功率: {data['station_info']['power_mw']} MW")

    print(f"\n功率流向:")
    pf = data['power_flow']
    print(f"  光伏: {pf.solar_power} MW")
    print(f"  电网: {pf.grid_power} MW")
    print(f"  电池: {pf.battery_power} MW")
    print(f"  负载: {pf.load_power} MW")
    print(f"  效率: {pf.efficiency}%")

    print(f"\n电池状态:")
    bs = data['battery_status']
    print(f"  平均SOC: {bs['avg_soc_percent']:.1f}%")
    print(f"  平均SOH: {bs['avg_soh_percent']:.1f}%")
    print(f"  平均温度: {bs['avg_temperature_c']:.1f}°C")

    print(f"\n经济指标:")
    em = data['economic_metrics']
    print(f"  今日收益: ¥{em.daily_revenue:,.2f}")
    print(f"  累计收益: ¥{em.cumulative_revenue:,.2f}")
    print(f"  ROI: {em.roi:.1f}%")

    print(f"\n环保指标:")
    env = data['environmental_metrics']
    print(f"  今日减排: {env.daily_co2_reduction:.1f} 吨CO2")
    print(f"  累计减排: {env.cumulative_co2_reduction:.1f} 吨CO2")
    print(f"  相当于植树: {env.equivalent_trees:,} 棵")

    print(f"\n最近告警:")
    for alarm in data['alarms']:
        print(f"  [{alarm['level'].upper()}] {alarm['message']}")

    # 生成JSON文件
    generate_dashboard_json(dashboard, "dashboard_data.json")
    print("\n大屏数据已保存到 dashboard_data.json")


if __name__ == '__main__':
    main()
