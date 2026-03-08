# 析锂延寿Workflow

> 版本：V1.0
> Meta-Workflow类型：寿命优化
> 核心目标：检测并抑制析锂，降低衰减率30%

---

## 应用场景

- 电动营运车辆（出租车、网约车、物流车）
- 快充站（超充、快充）
- 低温充电（北方冬季、高海拔地区）
- 高性能电动汽车

---

## 核心目标

- 析锂检测准确率 > 90%
- 析锂抑制成功率 > 85%
- 电池衰减率降低 > 30%
- 充电效率损失 < 10%

---

## Workflow DAG

```
      [充电数据采集]
             │
             ↓
      [B2.5:析锂检测]
             │
             ├─→ [无析锂] ──→ [正常充电策略]
             │
             ├─→ [轻微析锂] ──→ [B2.1:MCC降流]
             │                       │
             │                       ↓
             │                  [B2.6:MPC热管理]
             │                       │
             │                       ↓
             │                  [持续监测]
             │
             └─→ [严重析锂] ──→ [脉冲充电修复]
                                     │
                                     ↓
                                [C3.7:ICA分析验证]
                                     │
                                     ↓
                                [调整下次充电策略]
```

---

## BAS配置

| BAS | 输入 | 输出 | 关键参数 | 触发条件 |
|-----|------|------|---------|---------|
| **B2.5** | I、T、SOC | Φanode | 析锂阈值Φ<0V | 充电时实时 |
| **B2.1** | 析锂风险 | 充电电流 | MCC等级（0.3C/0.5C/0.7C） | 检测到析锂 |
| **B2.6** | T、I | 冷却功率 | MPC预测时域30s | 析锂风险>中 |
| **C3.7** | 充电曲线 | dQ/dV峰值 | 峰值左移>50mV | 充电结束 |

---

## 智能充电策略

```python
def charging_strategy(anode_potential, battery_temp, soc):
    # 析锂风险评估
    plating_risk = assess_plating_risk(anode_potential, battery_temp)

    # 策略选择
    IF plating_risk == SEVERE:
        # 严重析锂：降流+冷却
        I_charge = 0.3C
        P_cooling = MAX
        action = "脉冲充电修复"

    ELIF plating_risk == MODERATE:
        # 轻微析锂：适度降流
        I_charge = 0.5C
        P_cooling = MPC_predict(battery_temp, I_charge)
        action = "MCC策略"

    ELSE:  # plating_risk == NONE
        # 无析锂：最大化充电速度
        I_charge = 0.7C
        P_cooling = MIN
        action = "正常快充"

    # 充电末端：去极化修复
    IF soc > 90%:
        add_negative_pulse(duration=10s)

    return {
        'current': I_charge,
        'cooling': P_cooling,
        'action': action
    }
```

---

## 析锂风险评估

| 风险等级 | Φanode阈值 | 温度条件 | 充电电流 | 处置策略 |
|---------|-----------|---------|---------|---------|
| **无风险** | Φ > 0.05V | T > 15°C | 正常充电 | 继续监控 |
| **轻微析锂** | -0.05V < Φ ≤ 0.05V | 5°C < T ≤ 15°C | 降流至0.5C | MCC+MPC |
| **严重析锂** | Φ ≤ -0.05V | T ≤ 5°C | 降流至0.3C | 脉冲修复 |

---

## 脉冲充电修复方案

```python
def pulse_repair():
    """
    脉冲充电修复析锂
    原理：负脉冲使沉积的锂离子重新嵌入石墨
    """
    # Step 1: 检测到严重析锂
    IF plating_detected == SEVERE:
        # Step 2: 停止正向充电
        stop_charging()

        # Step 3: 施加负脉冲
        FOR i IN range(5):  # 5个脉冲周期
            discharge_pulse(duration=2s, current=-0.5C)
            rest(duration=1s)

        # Step 4: 恢复小电流充电
        resume_charging(current=0.2C)

        # Step 5: 逐步提升电流
        WHILE no_plating_detected:
            current += 0.1C
            IF current >= target_current:
                BREAK
```

---

## 执行效果示例

| 指标 | 优化前 | 优化后 | 提升 |
|-----|-------|-------|------|
| **平均充电时间** | 2.5小时 | 1.6小时 | ↓ 36% |
| **冬季容量衰减率** | 8%/月 | 5.5%/月 | ↓ 31% |
| **析锂发生率** | 45% | 12% | ↓ 73% |
| **营运车辆可用率** | 78% | 94% | ↑ 21% |

---

## 适用电池类型

- NCM（三元锂）- 最适用
- LFP（磷酸铁锂）- 低温场景适用
- NCA（三元锂）
- 石墨负极电池

**不适用**：
- 钛酸锂（LTO）- 无析锂问题
- 硅碳负极 - 需特殊算法

---

## 温度补偿策略

| 温度范围 | 析锂阈值调整 | 充电电流限制 | 冷却策略 |
|---------|-------------|-------------|---------|
| T > 25°C | Φ < 0V | 0.7C | 自然冷却 |
| 15°C < T ≤ 25°C | Φ < -0.02V | 0.5C | 弱冷却 |
| 5°C < T ≤ 15°C | Φ < -0.05V | 0.3C | 强冷却 |
| T ≤ 5°C | 禁止快充 | 0.2C | 预热+强冷却 |

---

## 延伸阅读

- [B2.5 析锂检测](../../资源/BAS-Skills目录.md#B25-析锂检测)
- [B2.1 MCC充电控制](../../资源/BAS-Skills目录.md#B21-MCC充电控制)
- [B2.6 MPC热管理](../../资源/BAS-Skills目录.md#B26-MPC热管理)
- [C3.7 ICA增量分析](../../资源/BAS-Skills目录.md#C37-ICA增量分析)
