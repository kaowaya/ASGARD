"""
I5.7 碳排放追踪系统 - 核心算法实现

储能系统全生命周期碳排放追踪与核算，支持LCA、碳交易、ESG报告。
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class CarbonFootprint:
    """碳足迹"""
    material_kg: float
    manufacturing_kg: float
    transportation_kg: float
    operational_kg: float
    recycling_kg: float
    total_kg: float
    carbon_reduction_kg: float
    net_carbon_kg: float


@dataclass
class CarbonIntensity:
    """碳强度"""
    value_g_kwh: float
    timestamp: datetime
    source: str  # grid/renewable/battery


class CarbonTracker:
    """碳排放追踪器"""

    def __init__(self, config: Dict):
        self.config = config

        # 碳排放因子（kg CO2e/unit）
        self.emission_factors = {
            # 材料（kg CO2e/kg）
            'lithium': 15.2,
            'nickel': 12.5,
            'cobalt': 25.0,
            'manganese': 2.5,
            'lfp_cathode': 8.0,
            'ncm_cathode': 18.0,
            'graphite': 3.5,
            'electrolyte': 5.0,
            'separator': 6.0,
            'copper_foil': 2.5,
            'aluminum_foil': 2.0,

            # 能源（kg CO2e/kWh）
            'grid_china_avg': 0.55,
            'grid_renewable': 0.02,
            'solar_pv': 0.04,

            # 运输（kg CO2e/ton-km）
            'truck': 0.1,
            'ship': 0.03,
            'rail': 0.02
        }

        # 电池材料组成（kg/kWh）
        self.battery_composition = {
            'NCM': {
                'ncm_cathode': 3.5,
                'graphite': 1.5,
                'electrolyte': 1.2,
                'separator': 0.3,
                'copper_foil': 1.0,
                'aluminum_foil': 0.8
            },
            'LFP': {
                'lfp_cathode': 4.0,
                'graphite': 1.5,
                'electrolyte': 1.2,
                'separator': 0.3,
                'copper_foil': 1.0,
                'aluminum_foil': 0.8
            }
        }

    def calculate_footprint(self,
                           station_id: str,
                           period: str,
                           battery_type: str = 'NCM',
                           capacity_kwh: float = 2000,
                           operation_data: Optional[pd.DataFrame] = None) -> CarbonFootprint:
        """
        计算碳足迹

        Args:
            station_id: 电站ID
            period: 核算周期（year/month/lifetime）
            battery_type: 电池类型
            capacity_kwh: 电池容量
            operation_data: 运行数据

        Returns:
            碳足迹结果
        """
        # 1. 原材料阶段
        material_carbon = self._calculate_material_carbon(battery_type, capacity_kwh)

        # 2. 生产制造阶段
        manufacturing_carbon = capacity_kwh * 30  # 30 kg CO2e/kWh

        # 3. 运输阶段
        transportation_carbon = capacity_kwh * 500 / 1000 * 0.05 * 1000  # 假设500km运输

        # 4. 运行阶段
        if operation_data is not None:
            operational_carbon = self._calculate_operational_carbon(operation_data)
            carbon_reduction = self._calculate_carbon_reduction(operation_data)
        else:
            # 估算
            annual_cycles = 365
            operational_carbon = capacity_kwh * annual_cycles * 0.55 / 0.95  # 电网充电
            carbon_reduction = capacity_kwh * annual_cycles * (0.55 - 0.02)  # 新能源替代

        # 5. 回收阶段（负值）
        recycling_carbon = -material_carbon * 0.5  # 50%材料回收

        total_carbon = (material_carbon + manufacturing_carbon +
                       transportation_carbon + operational_carbon +
                       recycling_carbon)

        net_carbon = total_carbon - carbon_reduction

        return CarbonFootprint(
            material_kg=material_carbon,
            manufacturing_kg=manufacturing_carbon,
            transportation_kg=transportation_carbon,
            operational_kg=operational_carbon,
            recycling_kg=recycling_carbon,
            total_kg=total_carbon,
            carbon_reduction_kg=carbon_reduction,
            net_carbon_kg=net_carbon
        )

    def _calculate_material_carbon(self, battery_type: str, capacity_kwh: float) -> float:
        """计算原材料碳排放"""
        composition = self.battery_composition.get(battery_type, {})
        total_carbon = 0

        for material, mass_per_kwh in composition.items():
            mass = mass_per_kwh * capacity_kwh
            emission_factor = self.emission_factors.get(material, 10)
            total_carbon += mass * emission_factor

        return total_carbon

    def _calculate_operational_carbon(self, operation_data: pd.DataFrame) -> float:
        """计算运行阶段碳排放"""
        total_carbon = 0

        for _, row in operation_data.iterrows():
            energy_kwh = row['grid_import_kwh']
            grid_factor = self.emission_factors.get('grid_china_avg', 0.55)
            total_carbon += energy_kwh * grid_factor

        return total_carbon

    def _calculate_carbon_reduction(self, operation_data: pd.DataFrame) -> float:
        """计算碳减排量"""
        # 新能源消纳减排
        renewable_energy = operation_data['solar_consumption_kwh'].sum()
        grid_factor = self.emission_factors.get('grid_china_avg', 0.55)
        renewable_factor = self.emission_factors.get('solar_pv', 0.04)
        renewable_reduction = renewable_energy * (grid_factor - renewable_factor)

        # 峰谷替代减排
        peak_shaving_reduction = operation_data['peak_shaving_kwh'].sum() * 0.2  # 边际减排

        total_reduction = renewable_reduction + peak_shaving_reduction

        return total_reduction

    def get_real_time_carbon_intensity(self, time: datetime) -> CarbonIntensity:
        """
        获取实时碳强度

        Args:
            time: 时间

        Returns:
            碳强度
        """
        # 简化：根据小时获取电网碳强度
        hour = time.hour

        # 白天碳强度低（光伏多）
        if 6 <= hour <= 18:
            intensity = 0.45  # g CO2e/kWh
            source = 'grid_solar_mix'
        else:
            intensity = 0.65  # g CO2e/kWh
            source = 'grid_fossil_mix'

        return CarbonIntensity(
            value_g_kwh=intensity * 1000,  # 转换为g
            timestamp=time,
            source=source
        )

    def generate_esg_report(self, station_id: str, year: int) -> Dict:
        """
        生成ESG报告数据

        Args:
            station_id: 电站ID
            year: 年份

        Returns:
            ESG报告数据
        """
        footprint = self.calculate_footprint(
            station_id=station_id,
            period=str(year),
            capacity_kwh=2000
        )

        report = {
            'station_id': station_id,
            'year': year,
            'carbon_footprint': {
                'total_emissions_tonnes': footprint.total_kg / 1000,
                'carbon_reduction_tonnes': footprint.carbon_reduction_kg / 1000,
                'net_emissions_tonnes': footprint.net_carbon_kg / 1000,
                'intensity_g_kwh': footprint.net_carbon_kg / (2000 * 365) * 1000
            },
            'esg_metrics': {
                'carbon_neutral': footprint.net_carbon_kg <= 0,
                'sdg_alignment': ['SDG7', 'SDG13'],
                'taxonomy_eligible': True
            },
            'recommendations': [
                '增加绿电采购比例',
                '参与碳交易市场',
                '发布碳中和路线图'
            ]
        }

        return report


def main():
    """演示"""
    print("I5.7 碳排放追踪系统")

    tracker = CarbonTracker({})

    # 碳足迹核算
    print("\n碳足迹核算:")
    footprint = tracker.calculate_footprint(
        station_id="STATION_001",
        period="2025",
        battery_type="NCM",
        capacity_kwh=2000
    )

    print(f"  原材料阶段: {footprint.material_kg:.0f} kg CO2e")
    print(f"  制造阶段: {footprint.manufacturing_kg:.0f} kg CO2e")
    print(f"  运输阶段: {footprint.transportation_kg:.0f} kg CO2e")
    print(f"  运行阶段: {footprint.operational_kg:.0f} kg CO2e")
    print(f"  回收阶段: {footprint.recycling_kg:.0f} kg CO2e")
    print(f"  总排放: {footprint.total_kg/1000:.1f} 吨 CO2e")
    print(f"  碳减排: {footprint.carbon_reduction_kg/1000:.1f} 吨 CO2e")
    print(f"  净排放: {footprint.net_carbon_kg/1000:.1f} 吨 CO2e")

    # 实时碳强度
    print("\n实时碳强度:")
    intensity = tracker.get_real_time_carbon_intensity(datetime.now())
    print(f"  碳强度: {intensity.value_g_kwh:.0f} g CO2e/kWh")
    print(f"  来源: {intensity.source}")

    # ESG报告
    print("\nESG报告数据:")
    report = tracker.generate_esg_report("STATION_001", 2025)
    print(f"  净排放: {report['carbon_footprint']['net_emissions_tonnes']:.1f} 吨 CO2e")
    print(f"  碳中和: {'是' if report['esg_metrics']['carbon_neutral'] else '否'}")
    print(f"  符合分类法: {'是' if report['esg_metrics']['taxonomy_eligible'] else '否'}")


if __name__ == "__main__":
    main()
