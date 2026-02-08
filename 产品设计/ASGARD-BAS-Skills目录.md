# ASGARD BAS Skills 目录

> 版本：V1.0
> 日期：2026-02-07
> 覆盖范围：全产业链五层工具箱 × 5种电池类型
>
> **什么是BAS？**
> BAS（Battery Algorithm Skills）= 电池算法技能包，是ASGARD平台中可被Agent动态加载、训练和组合的算法模板。
>
> **BAS结构**：
> ```
> skill-name/
> ├── SKILL.md              # 必需：技能说明（YAML frontmatter + Markdown）
> ├── templates/            # 算法模板（Python/C++代码框架）
> ├── reference/            # 参考文档（理论、参数调优、电池映射）
> └── data_samples/         # 示例数据（可选）
> ```

---

## 目录结构

```
├── L1 生产层级Skills（Manufacturing Tier）
│   ├── M1.1 极片缺陷AI检测（defect-detection-yolo）
│   ├── M1.2 电芯OCV内阻分级（cell-grading-clustering）
│   ├── M1.3 组装一致性控制（assembly-consistency-gpr）
│   ├── M1.4 注液量优化（electrolyte-optimization-eis）
│   ├── M1.5 化成曲线异常检测（formation-anomaly-ica）
│   └── M1.6 固态界面质量评估（solid-interface-eis）
├── L2 BMS层级Skills（BMS Tier）
│   ├── B2.1 SOC估计-DAEKF（soc-estimation-daekf）
│   ├── B2.2 SOH估计-ICA片段（soh-estimation-ica）
│   ├── B2.3 SOP估计-功率边界（sop-estimation-power）
│   ├── B2.4 智能均衡优化（active-balancing-mpc）
│   ├── B2.5 析锂检测-简化模型（lithium-plating-detection）
│   ├── B2.6 热管理-MPC（thermal-management-mpc）
│   ├── B2.7 主动安全控制（active-safety-l0l4）
│   ├── B2.8 钠电分段滤波（sodium-ion-filtering）
│   └── B2.9 固态压力监测（solid-state-pressure）
├── L3 云端层级Skills（Cloud Tier）
│   ├── C3.1 内短路诊断-SOS（internal-short-sos）
│   ├── C3.2 热失控预警-MEMS（thermal-runaway-mems）
│   ├── C3.3 寿命预测-RUL（lifetime-prediction-ode）
│   ├── C3.4 异常检测-香农熵（anomaly-detection-shannon）
│   ├── C3.5 SOH-XGBoost集成（soh-prediction-xgboost）
│   ├── C3.6 温度场重构（temperature-field-reconstruction）
│   ├── C3.7 ICA深度分析（ica-deep-analysis）
│   ├── C3.8 EIS谱图分析（eis-spectrum-analysis）
│   ├── C3.9 固态界面失效（solid-interface-failure）
│   └── C3.10 钠电自放电补偿（sodium-self-discharge）
├── L4 应用层级Skills（Application Tier）
│   ├── A4.1 电动汽车充电优化（ev-charging-optimization）
│   └── A4.2 家庭储能优化（home-storage-optimization）
└── L5 工商业层级Skills（Industrial Tier）
    ├── I5.1 微网能量管理（microgrid-energy-management）
    ├── I5.2 V2G双向优化（v2g-bidirectional-optimization）
    ├── I5.3 工厂配储优化（factory-storage-optimization）
    ├── I5.4 虚拟电站VPP（virtual-power-plant）
    ├── I5.5 储能电站资产评估（asset-valuation-rul）
    ├── I5.6 电池回收决策（battery-recycling-decision）
    └── I5.7 碳排放追踪（carbon-footprint-tracking）
```

---

## BAS Skills详细说明

每个BAS Skill遵循Agent Skills标准格式（[spec](https://agentskills.io/specification)），包含以下部分：

### 标准SKILL.md结构

```yaml
---
name: skill-name
description: A clear description of what this skill does and when to use it.
metadata:
  version: "1.0"
  author: ASGARD
  battery_types: [LFP, NCM, Na-ion, Semi-Solid, Solid-State]
  tier: L1/L2/L3/L4/L5
  compute_requirement: <10MHz / <50MHz / <100MHz / Cloud
  pricing: Free / Pro / Enterprise
---

# Skill Name

## When to use this skill
Use this skill when [specific scenarios and use cases]...

## How it works
[Explanation of the algorithm, theory, and methodology]

## Inputs
- [Input data format and requirements]

## Outputs
- [Output format and what to expect]

## Parameters
| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| param1 | 0.5 | 0.1-1.0 | Description... |

## Battery Type Compatibility
| Battery Type | Support Level | Notes |
|-------------|--------------|-------|
| LFP | ✅ Full | Default configuration |
| NCM | ✅ Full | Peak positions at 3.65/3.80/3.95V |
| Na-ion | ⚠️ Partial | Requires calibration |
| Solid-State | ⚠️ Partial | Use alternative skill M1.6 |

## Training Requirements
- [Minimum data requirements]
- [Training time estimation]
- [Recommended hyperparameters]

## References
- [Link to reference documentation]
- [Academic papers]

## Changelog
- v1.0 (2026-02-07): Initial release
```

---

## L1 生产层级Skills（Manufacturing Tier）

---

## L1 生产层级算法（Manufacturing Tier）

### M1.1 质量控制算法

#### 🔬 M1.1.1 极片缺陷AI检测

| 属性 | 值 |
|-----|---|
| **算法类型** | 计算机视觉 + 深度学习 |
| **核心模型** | YOLOv8 / Mask R-CNN |
| **输入数据** | 极片涂布图像（高分辨率线扫描） |
| **输出结果** | 缺陷类别 + 位置 + 严重程度评分 |
| **检测精度** | 漏检率 <0.1%, 误检率 <1% |
| **处理速度** | 实时（>30m/min线速度） |
| **电池类型复用** | ✅ 100%通用 |
| **部署位置** | 边缘端（生产线工控机） |

**检测缺陷类别**：
- 针孔（Pinhole）
- 划痕（Scratch）
- 涂布厚度不均（Coating Thickness Variation）
- 颗粒异物（Foreign Particle）
- 边缘缺损（Edge Defect）

**算法流程**：
```
极片图像采集
    ↓
预处理（去噪、对比度增强）
    ↓
特征提取（CNN自动特征）
    ↓
缺陷检测与分类
    ↓
严重程度评分
    ↓
实时反馈至涂布机
```

**可复用框架**：
- 模型架构：YOLO/Mask R-CNN（跨体系通用）
- 训练策略：迁移学习（仅需替换缺陷样本数据）
- 后处理逻辑：通用缺陷评分规则

---

#### 📊 M1.1.2 电芯OCV内阻分级

| 属性 | 值 |
|-----|---|
| **算法类型** | 无监督聚类 + 异常检测 |
| **核心模型** | DBSCAN + Isolation Forest |
| **输入数据** | OCV（开路电压）、DCIR（直流内阻）、K值（电压降） |
| **输出结果** | A/B/C等级分级 + 自放电率预测 |
| **分级精度** | 95%+ 与实际自放电率吻合 |
| **电池类型复用** | ✅ 100%通用（阈值需标定） |
| **部署位置** | 云端（批量分析） |

**算法原理**：
1. **OCV-DCIR相关性建模**：建立正常电芯的OCV与DCIR分布
2. **异常电芯识别**：Isolation Forest识别离群点（潜在高自放电）
3. **聚类分级**：DBSCAN将电芯分为3个等级
   - A级：自放电率 <2%/月
   - B级：自放电率 2-5%/月
   - C级：自放电率 >5%/月（剔除）

**跨体系适配**：
- 算法框架：100%通用
- 标定参数：聚类半径ε、最小样本数MinPts需根据电池类型调整

---

#### ⚡ M1.1.3 组装一致性控制

| 属性 | 值 |
|-----|---|
| **算法类型** | 回归分析 + 优化算法 |
| **核心模型** | 高斯过程回归（GPR）+ 贝叶斯优化 |
| **输入数据** | 压装力、内阻、模组电压差 |
| **输出结果** | 最优压装力参数 |
| **优化目标** | 模组内阻差异最小化 |
| **电池类型复用** | ✅ 100%通用 |
| **部署位置** | 边缘端（模组组装线） |

**算法流程**：
```
压装力 → 内阻响应建模（GPR）
    ↓
建立压装力-内阻传递函数
    ↓
贝叶斯优化搜索最优压装力
    ↓
实时反馈至压装机
```

---

### M1.2 异常检测算法

#### 🔍 M1.2.1 化成曲线异常检测

| 属性 | 值 |
|-----|---|
| **算法类型** | 时序异常检测 + ICA分析 |
| **核心模型** | One-Class SVM + dQ/dV峰值提取 |
| **输入数据** | 首次充电曲线（V-I-T时序） |
| **输出结果** | 正常/异常判定 + 异常类型分类 |
| **检测精度** | 98%+（验证集） |
| **电池类型复用** | ⚠️ 框架通用，峰值位置需标定 |
| **部署位置** | 云端（批量分析） |

**检测异常类型**：
1. 微短路（Micro-short）：充电阶段电压异常波动
2. 析锂（Lithium Plating）：dQ/dV低电位异常峰
3. 电解液不足（Insufficient Electrolyte）：阻抗过早上升
4. SEI膜异常（SEI Anomaly）：首效偏差 >5%

**ICA特征提取**：
```
充充电曲线（V-I）
    ↓
计算 dQ/dV
    ↓
峰值提取（Peak Detection）
    ↓
与标准模板对比（Template Matching）
    ↓
异常判定
```

**跨体系适配**：
- LFP：3.35V / 3.45V 峰值
- NCM：3.65V / 3.80V / 3.95V 峰值
- Na-ion：待标定（硬碳平台特征）
- 固态：待标定（界面阻抗特征）

---

### M1.3 工艺优化算法

#### 💧 M1.3.1 注液量优化

| 属性 | 值 |
|-----|---|
| **算法类型** | EIS反演 + 优化算法 |
| **核心模型** | 等效电路模型（ECM）拟合 + 梯度下降 |
| **输入数据** | EIS谱图（注液后不同时间点） |
| **输出结果** | 最优注液量 + 浸润度评估 |
| **电池类型复用** | ✅ 液态电池通用（LFP/NCM/Na-ion） |
| **部署位置** | 云端 + 边缘端 |

**算法原理**：
1. **EIS谱图拟合**：提取电荷转移阻抗Rct
2. **浸润度评估**：Rct随时间下降速率
3. **最优注液量**：平衡浸润度 vs 成本

**固态电池替代方案**：M1.6 固态界面质量评估

---

#### 🔒 M1.3.2 固态界面质量评估

| 属性 | 值 |
|-----|---|
| **算法类型** | EIS反演 + 界面接触建模 |
| **核心模型** | 固态等效电路（固-固界面阻抗） |
| **输入数据** | EIS谱图 + 压力数据 |
| **输出结果** | 界面接触质量评分 |
| **电池类型复用** | ✅ 半固态/全固态通用 |
| **部署位置** | 云端 |

**固态等效电路**：
```
[Cathode] | [Solid Electrolyte] | [Anode]
              ↓
        Interface Impedance (Z_int)
              ↓
    Contact Quality = f(Z_int, Pressure)
```

---

## L2 BMS层级算法（BMS Tier）

### B2.1 SOX状态估计算法

#### 🔋 B2.1.1 SOC估计 - DAEKF（双自适应扩展卡尔曼滤波）

| 属性 | 值 |
|-----|---|
| **算法类型** | 状态-参数联合估计 |
| **核心模型** | 双EKF并行：状态EKF + 参数EKF |
| **输入数据** | 电流I、电压V、温度T |
| **输出结果** | SOC + 欧姆内阻R₀ + 极化电容Cp |
| **估计精度** | SOC误差 ≤5% |
| **更新频率** | 10Hz |
| **算力需求** | <10MHz（ARM Cortex-M4可运行） |
| **电池类型复用** | ✅ 100%通用（参数需标定） |
| **部署位置** | BMS板端 |

**算法流程**：
```
┌─────────────────────────────────────────────┐
│  状态EKF（State EKF）                       │
│  - 状态方程：SOC(k+1) = SOC(k) - IΔt/Cn     │
│  - 观测方程：V = OCV(SOC) - I*R0 - Vp       │
│  - 输出：SOC估计值                          │
└─────────────────────────────────────────────┘
                    ↓ 协同
┌─────────────────────────────────────────────┐
│  参数EKF（Parameter EKF）                   │
│  - 参数辨识：R₀、Cp在线更新                 │
│  - 遗忘因子λ：动态调节历史数据权重          │
│  - 输出：实时模型参数                       │
└─────────────────────────────────────────────┘
```

**关键创新点**：
1. **遗忘因子λ**：检测工况突变时，加速模型收敛
2. **温度补偿**：R₀(T)、Cp(T)查表插值
3. **老化适配**：R₀(SOH)随容量衰减动态调整

**跨体系适配**：
- OCV-SOC曲线：需根据电池类型标定
- ECM参数：R₀、Cp、Rp初值不同
- 算法框架：100%通用

**嵌入式实现**：
```c
// 伪代码示例
void DAEKF_Update(float I, float V, float T) {
    // 状态预测
    SOC_pred = SOC_prev - I * dt / Cn;

    // 参数更新（带遗忘因子）
    lambda = detect_transient(I, V) ? 0.9 : 0.99;
    R0 = update_parameter(R0, V, I, lambda);
    Cp = update_parameter(Cp, V, I, lambda);

    // 状态更新
    SOC = update_state(SOC_pred, V, I, R0, Cp);
}
```

---

#### 📈 B2.1.2 SOH估计 - ICA片段分析

| 属性 | 值 |
|-----|---|
| **算法类型** | 增量容量分析 + 机器学习 |
| **核心模型** | dQ/dV峰值提取 + XGBoost回归 |
| **输入数据** | 片段充电曲线（10%电量区间） |
| **输出结果** | SOH + 不确定性估计 |
| **估计精度** | SOH误差 ≤1.5% |
| **更新频率** | 每次充电 |
| **算力需求** | <50MHz |
| **电池类型复用** | ⚠️ 框架通用，峰值位置需标定 |
| **部署位置** | BMS板端 + 云端协同 |

**算法流程**：
```
片段充电数据（V-I-T，10% SOC区间）
    ↓
dQ/dV计算（数值微分 + 低通滤波）
    ↓
峰值提取（Peak Detection）
    ↓
特征工程：
  - 峰值位置（Peak Position）
  - 峰值高度（Peak Height）
  - 峰值面积（Peak Area）
  - 峰值左移量（Left Shift）
    ↓
XGBoost回归 → SOH估计
```

**关键特征**：
| 特征 | 物理意义 | 与老化关联 |
|-----|---------|-----------|
| 主峰位置 | 石墨相变电位 | 左移 >50mV → 析锂风险 |
| 峰值高度 | 活性锂量 | 下降 → LLI（活性锂损失） |
| 峰值面积 | 嵌锂容量 | 减少 → LAM（活性物质损失） |

**跨体系适配**：
| 电池类型 | ICA峰值位置 | 标定需求 |
|---------|------------|---------|
| LFP | 3.35V / 3.45V | 低 |
| NCM | 3.65V / 3.80V / 3.95V | 中 |
| Na-ion | 待标定 | 高（需实验） |
| 固态 | 待标定 | 高（需实验） |

---

#### ⚡ B2.1.3 SOP估计 - 功率边界预测

| 属性 | 值 |
|-----|---|
| **算法类型** | 约束优化 |
| **核心模型** | 多约束功率边界计算 |
| **输入数据** | SOC、温度、SOH |
| **输出结果** | 最大充/放电功率（10s/30s/持续） |
| **更新频率** | 1Hz |
| **算力需求** | <10MHz |
| **电池类型复用** | ✅ 100%通用（约束需标定） |
| **部署位置** | BMS板端 |

**约束条件**：
1. **电压约束**：V_min ≤ V ≤ V_max
2. **电流约束**：I_min ≤ I ≤ I_max
3. **功率约束**：P ≤ P_max（BMS硬件限制）
4. **温度约束**：T ≤ T_max
5. **SOC约束**：SOC_min ≤ SOC ≤ SOC_max
6. **析锂约束**：Φanode ≥ 0V（锂电池专用）

**优化目标**：
```
Maximize P_charge / P_discharge
Subject to:
    V(SOC, I, T) within limits
    Φanode(I, T, SOC) ≥ 0V  // 锂电池
    dT/dt ≤ cooling_capacity // 热约束
```

---

### B2.2 均衡控制算法

#### 🔄 B2.2.1 智能均衡优化

| 属性 | 值 |
|-----|---|
| **算法类型** | 多目标优化 |
| **核心模型** | 模型预测控制（MPC） |
| **输入数据** | 电芯电压差、SOC差、均衡器状态 |
| **输出结果** | 均衡开关序列 |
| **优化目标** | Min(能量损失 + 均衡时间 + 开关次数) |
| **算力需求** | <50MHz |
| **电池类型复用** | ✅ 100%通用 |
| **部署位置** | BMS板端 |

**目标函数**：
```
J = w1 * EnergyLoss + w2 * BalanceTime + w3 * SwitchCount
    ↓
Minimize J
Subject to:
    ΔSOC ≤ 2%
    均衡电流 ≤ I_bal_max
    开关频率 ≤ f_max
```

**传统方法 vs ASGARD方法**：
| 方法 | 策略 | 缺点 | ASGARD优势 |
|-----|------|------|-----------|
| 简单削峰填谷 | 电压最高电芯放电 | 未考虑能耗与开关损耗 | 多目标优化 |
| 固定时间均衡 | 周期性触发 | 无法应对动态工况 | 实时MPC预测 |
| 阈值触发 | ΔV > 10mV | 响应滞后 | 预测性触发 |

---

### B2.3 热管理算法

#### 🌡️ B2.3.1 模型预测控制（MPC）

| 属性 | 值 |
|-----|---|
| **算法类型** | 模型预测控制 |
| **核心模型** | 热模型 + 预测优化 |
| **输入数据** | 当前温度、环境温度、负载预测 |
| **输出结果** | 冷却功率设定值 |
| **预测时域** | 30-60s |
| **控制精度** | ±1°C |
| **算力需求** | <100MHz |
| **电池类型复用** | ✅ 100%通用（热参数需标定） |
| **部署位置** | BMS板端或热管理控制器 |

**热模型**：
```
C_th * dT/dt = Q_gen - Q_diss
    ↓
Q_gen = I² * R0 + I * |Φ_overpotential| + Q_entropy
Q_diss = h * A * (T_cell - T_ambient)
```

**MPC优化**：
```
For each time step k = 0 to N:
    Predict T_cell(k+1) using thermal model
    Optimize cooling power P_cool(k)
    Minimize: Σ ||T_cell(k) - T_target||² + λ * P_cool(k)²
    ↓
Apply first control input
Repeat at next time step
```

---

### B2.4 安全控制算法

#### ⚠️ B2.4.1 主动安全控制（L0-L4分级）

| 属性 | 值 |
|-----|---|
| **算法类型** | 规则引擎 + 有限状态机 |
| **核心模型** | 多级响应决策树 |
| **输入数据** | 故障诊断结果（L1-L4评分） |
| **输出结果** | 安全控制动作 |
| **响应时间** | <100ms（L4紧急级） |
| **电池类型复用** | ✅ 100%通用 |
| **部署位置** | BMS板端 |

**分级响应机制**：
```
┌──────────────────────────────────────────────────────┐
│ L0 [0-20分]：绿灯·正常                              │
│   → 动作：无限制运行                                 │
│   → 监控：1Hz采样                                    │
└──────────────────────────────────────────────────────┘
                      ↓ 故障评分累计
┌──────────────────────────────────────────────────────┐
│ L1 [20-40分]：黄灯·关注                            │
│   → 动作：后台记录，10Hz高频监控                     │
│   → 用户：APP通知（非打扰）                          │
└──────────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────┐
│ L2 [40-60分]：橙灯·预警                            │
│   → 动作：限流0.5C / 限压4.15V                       │
│   → 用户：APP弹窗 + 短信通知                         │
└──────────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────┐
│ L3 [60-80分]：红灯·告警                            │
│   → 动作：禁止充电 / 限制放电0.2C                    │
│   → 用户：强制弹窗 + 电话通知                        │
└──────────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────┐
│ L4 [80-100分]：闪红·紧急                           │
│   → 动作：断开继电器（主回路+预充）                 │
│   → 用户：紧急电话 + 自动报警                        │
│   → 响应时间：<100ms                                 │
└──────────────────────────────────────────────────────┘
```

**规则引擎核心规则**（见产品差异化文档02章节）：
- IF 自放电率 > 5%/月 THEN +30分
- IF 充电电压突降 THEN +40分
- IF 温度突升 >10°C THEN +50分
- IF 内阻增长率 >50% THEN +20分
- IF 容量衰减 <80% THEN +15分
- IF SOC跳变 THEN +25分

---

#### 🔍 B2.4.2 析锂检测 - 简化模型

| 属性 | 值 |
|-----|---|
| **算法类型** | 电化学模型简化 |
| **核心模型** | 负极电位实时计算 |
| **输入数据** | 电流I、温度T、SOC |
| **输出结果** | 负极电位Φanode |
| **检测精度** | Φanode误差 <20mV |
| **预警条件**：Φanode < 0V |
| **算力需求** | <20MHz |
| **电池类型复用** | ✅ 锂电池通用（LFP/NCM） |
| **部署位置** | BMS板端 |

**算法原理**：
```
Φanode = Φocv_anode(SOC_anode) - I * R_anode - η_concentration
    ↓
简化为：
Φanode ≈ f(I, T, SOC)  // 查表 + 插值
    ↓
预警条件：
IF Φanode < 0V THEN 析锂风险 → 触发L2/L3预警
```

**三电极实验标定**：
1. 构建无析锂负极电位图谱（Map）
2. 建立Φanode = f(I, T, SOC)查表
3. BMS运行简化模型

---

#### 🧪 B2.4.3 钠电分段滤波

| 属性 | 值 |
|-----|---|
| **算法类型** | 自适应加权滤波 |
| **核心模型** | 斜坡区OCV加权 + 平台区安时积分 |
| **输入数据** | 电流I、电压V、温度T |
| **输出结果** | SOC |
| **适用场景** | 钠离子电池硬碳负极特性 |
| **电池类型复用** | ✅ 钠离子专用 |
| **部署位置** | BMS板端 |

**算法原理**：
```
IF V in slope_region (高电位斜坡区):
    SOC = α * SOC_OCV + (1-α) * SOC_Coulomb  // α > 0.5
ELSE IF V in plateau_region (低电位平台区):
    SOC = β * SOC_OCV + (1-β) * SOC_Coulomb  // β < 0.3
ELSE:
    SOC = γ * SOC_OCV + (1-γ) * SOC_Coulomb  // γ = 0.5
```

**钠离子硬碳特性**：
- 高电位斜坡区：电压敏感，OCV估计准确
- 低电位平台区：电压平坦，安时积分为主

---

#### 🎯 B2.4.4 固态压力监测

| 属性 | 值 |
|-----|---|
| **算法类型** | 时序异常检测 |
| **核心模型** | 呼吸效应模式识别 |
| **输入数据** | 压力传感器数据 + 电压V + 电流I |
| **输出结果** | 界面失效预警 |
| **电池类型复用** | ✅ 半固态/全固态专用 |
| **部署位置** | BMS板端 |

**呼吸效应异常检测**：
```
正常呼吸效应：压力 ↔ SOC可逆变化
异常模式：
  - 压力突降 → 界面剥离
  - 压力持续上升 → 气体生成
  - 压力-SOC滞后增大 → 界面退化
```

---

## L3 云端层级算法（Cloud Tier）

### C3.1 故障诊断算法

#### 🔥 C3.1.1 内短路诊断 - SOS基因图谱

| 属性 | 值 |
|-----|---|
| **算法类型** | 电化学模型 + 数据驱动 |
| **核心模型** | 漏电流等效电路 + 基因演化追踪 |
| **输入数据** | 电芯电压历史、温度历史、充电曲线 |
| **输出结果** | 漏电流大小、短路电阻Risc、置信度 |
| **检测精度**：漏电流 <10mA |
| **覆盖率**：96.4%（低电流隐患） |
| **电池类型复用** | ✅ 100%通用 |
| **部署位置** | 云端API |

**算法原理**：
```
Step 1: 建立理想电压模型
    V_ideal = OCV(SOC) - I * R_healthy
    ↓
Step 2: 计算残差
    Residual = V_measured - V_ideal
    ↓
Step 3: 双信号融合
    容量维度：ΔSOC异常 → 自放电
    热力学维度：温度异常 → 焦耳热
    ↓
Step 4: 漏电流等效电路
    I_leak = V / (R_cell || R_isc)
    → 反推 R_isc
    ↓
Step 5: SOS基因演化
    追踪每个电芯的衰减轨迹
    区分先天差异 vs 后天突变
```

**双信号融合优势**：
- 容量维度：捕捉微小电荷不一致（软短路敏感）
- 热力学维度：捕捉焦耳热引起的参数波动
- 两者互补，降低误报率

---

#### 📊 C3.1.2 异常检测 - 香农熵

| 属性 | 值 |
|-----|---|
| **算法类型** | 信息论 + 统计分析 |
| **核心模型** | 改进Z-分数离散化 |
| **输入数据** | 电芯电压差、温度差 |
| **输出结果** | 故障等级（正常/关注/预警/告警/紧急） |
| **抗噪性**：有效过滤电流波动和环境噪声 |
| **电池类型复用** | ✅ 100%通用 |
| **部署位置** | 云端API |

**算法流程**：
```
原始差值：ΔV_i = V_i - V_mean
    ↓
改进Z-分数离散化：
    Z_i = (ΔV_i - median) / MAD  // MAD = median(|ΔV_i - median|)
    ↓
离散化故障等级：
    Level = discretize(Z_i)
    ↓
香农熵计算：
    Entropy = -Σ p(Level) * log2(p(Level))
    ↓
系统有序度评估：
    Entropy ↓ → 系统有序 → 正常
    Entropy ↑ → 系统混乱 → 异常
```

**关键创新**：
- 不直接使用易波动的原始差值
- 通过改进Z-分数转化为离散故障等级
- 有效过滤电流波动和环境噪声

---

### C3.2 健康评估算法

#### 🧬 C3.2.1 SOH - XGBoost集成学习

| 属性 | 值 |
|-----|---|
| **算法类型** | 集成学习 + 迁移学习 |
| **核心模型** | XGBoost + 特征工程 |
| **输入数据**：ICA片段特征（10%充电区间） |
| **输出结果**：SOH + 不确定性 |
| **估计精度**：SOH误差 ≤1.5% |
| **更新频率**：每次充电 |
| **电池类型复用** | ⚠️ 框架通用，特征需工程化 |
| **部署位置**：云端训练 + 边缘推理 |

**特征工程**（15个核心特征）：
```
1. 自放电特征
   F1: 自放电速率（%/月）
   F2: 自放电加速度
   F3: SOC-OCV偏差

2. 充电异常特征
   F4: 充电电压平台偏移
   F5: 充电电压突降事件
   F6: 充电时间延长比例
   F7: 充电末期电压上升速率

3. 温度异常特征
   F8: 温度偏高（vs环境）
   F9: 温度梯度
   F10: 温度突升事件
   F11: 温度波动标准差

4. 内阻+SOC特征
   F12: 直流内阻DCIR
   F13: 内阻增长率
   F14: SOC跳变
   F15: 容量衰减率
```

**模型训练流程**：
```
云端大数据（10000+电芯全生命周期数据）
    ↓
特征工程 + 数据清洗
    ↓
XGBoost训练
    ↓
模型量化（32bit → 8bit）
    ↓
下发至边缘端
    ↓
边缘推理：实时SOH更新
```

---

#### 🔬 C3.2.2 ICA深度分析

| 属性 | 值 |
|-----|---|
| **算法类型**：增量容量分析 + 模式识别 |
| **核心模型**：dQ/dV峰值提取 + 聚类分类 |
| **输入数据**：完整充电曲线 |
| **输出结果**：老化模式分类（LLI/LAM/析锂/混合） |
| **电池类型复用** | ⚠️ 框架通用，峰值位置需标定 |
| **部署位置**：云端API |

**ICA峰值与老化机制关联**：
```
LFP (磷酸铁锂):
  Peak 1 (~3.35V): Stage IV → III
  Peak 2 (~3.45V): Stage III → II

NCM (三元锂):
  Peak 1 (~3.65V): Stage IV → III
  Peak 2 (~3.80V): Stage III → II  ⭐ 主峰
  Peak 3 (~3.95V): Stage II → I

老化模式识别:
  - 主峰左移 >50mV → 析锂
  - 峰值高度下降 → LLI（活性锂损失）
  - 峰值面积减小 → LAM（活性物质损失）
  - 低电位异常峰 → 严重析锂
```

**评分规则**：
- IF 峰值左移 >50mV THEN +40分
- IF 左移 >100mV THEN +30分
- IF 低电位异常峰 THEN +50分
- IF 峰值强度下降 >30% THEN +30分

---

#### 📈 C3.2.3 EIS谱图分析

| 属性 | 值 |
|-----|---|
| **算法类型**：阻抗谱拟合 + 界面追踪 |
| **核心模型**：等效电路模型（ECM）拟合 |
| **输入数据**：EIS Nyquist图 |
| **输出结果**：Rs、Rct、Cdl、Warburg系数 |
| **拟合精度**：R² > 0.95 |
| **电池类型复用** | ✅ 100%通用（电路结构需适配） |
| **部署位置**：云端API |

**等效电路模型**：
```
┌────────────────────────────────────────┐
│  Rs                                    │
│  ────[WWWWWW]────┐                     │
│                  │                     │
│                 [CPE]                  │
│                  │                     │
│                 [Rct]                  │
│                  │                     │
│                [Warburg]               │
└────────────────────────────────────────┘

Rs: 溶液电阻
Rct: 电荷转移电阻
CPE: 常相位元件（双电层）
Warburg: 扩散阻抗
```

**界面演化追踪**：
- Rct ↑ → SEI膜增厚或界面退化
- CPE变化 → 双电层结构变化
- Warburg系数 ↑ → 扩散受阻

---

### C3.3 寿命预测算法

#### 🔮 C3.3.1 RUL - 半物理ODE模型

| 属性 | 值 |
|-----|---|
| **算法类型**：半物理建模 + 参数拟合 |
| **核心模型**：dQ/dN = -kbase × (1 + fearly + fdive) |
| **输入数据**：历史容量衰减曲线 |
| **输出结果**：RUL（剩余循环次数）+ 置信区间 |
| **预测精度**：±5%（即使少量数据） |
| **电池类型复用** | ✅ 100%通用（参数需标定） |
| **部署位置**：云端API |

**半物理模型**：
```
dQ/dN = -k_base × (1 + f_early(N) + f_dive(N))
    ↓
f_early(N) = A_early × exp(-N/τ_early)
  → 模拟SEI膜形成初期的快速衰减
    ↓
f_dive(N) = S_scale × exp(k_dive × N)
  → 模拟寿命末期的容量"跳水"
```

**物理意义明确的参数**：
| 参数 | 物理意义 | 典型值（LFP） |
|-----|---------|--------------|
| k_base | 基础衰减速率 | 0.0002/循环 |
| A_early | 早期衰减幅度 | 0.02-0.05 |
| τ_early | 早期衰减时间常数 | 200-300循环 |
| S_scale | 跳水幅度 | 0.1-0.3 |
| k_dive | 跳水速率 | 0.005-0.01 |

**vs 纯数据驱动（LSTM）**：
| 对比项 | 半物理ODE | LSTM |
|-------|----------|------|
| 数据需求 | 小样本即可 | 大数据训练 |
| 可解释性 | 强（物理意义明确） | 弱（黑盒） |
| 泛化能力 | 高（跨体系通用） | 低（需重新训练） |
| 寿命拐点预测 | 准确 | 容易过拟合 |

---

### C3.4 热失控预警算法

#### 🚨 C3.4.1 热失控预警 - MEMS传感器阵列

| 属性 | 值 |
|-----|---|
| **算法类型**：多模态传感器融合 |
| **核心模型**：H₂/CO/VOCs浓度监测 + 时序逻辑 |
| **输入数据**：气体传感器数据 + 电压 + 温度 |
| **输出结果**：热失控预警等级（1/2/3级） |
| **预警提前量**：2-5分钟（比温控提前） |
| **电池类型复用** | ✅ 100%通用 |
| **部署位置**：边缘端 + 云端协同 |

**多模态融合**：
```
传感器阵列:
  - H₂传感器 → 热失控早期特征气体
  - CO传感器 → 电解液分解产物
  - VOCs传感器 → 电解液挥发成分
    ↓
时序逻辑:
  电压压差异常 → 温度异常 → 气体逸散 → 烟雾/明火
    ↓
预警层级:
  一级预警：电压异常（C3.1.1）
  二级预警：温度上升
  三级预警：气体逸散 ⭐ 关键
```

**终极防线**：
- 当电化学手段失效时，依靠物理产物（气体）进行最后预警
- 比温度传感器提前2-5分钟
- 联动消防系统精准喷淋

---

#### 🌡️ C3.4.2 温度场重构

| 属性 | 值 |
|-----|---|
| **算法类型**：热传导方程反演 |
| **核心模型**：导热解析方程 + 边界条件反推 |
| **输入数据**：表面温度 + 电流I |
| **输出结果**：中心温度T_center、温度梯度∇T |
| **预测精度**：±2°C |
| **电池类型复用** | ✅ 100%通用（热参数需标定） |
| **部署位置**：云端API |

**热传导方程**：
```
∂T/∂t = α (∂²T/∂x² + ∂²T/∂y² + ∂²T/∂z²) + Q_gen/(ρ·Cp)
    ↓
边界条件:
  表面温度: T_surface(t) [已知]
  产热功率: Q_gen = I²·R0 + I·|Φ_over| + Q_entropy
    ↓
反推中心温度:
  T_center(t) = f(T_surface, I, thermal_properties)
```

**应用价值**：
- 快充场景：提前数分钟预警中心过热
- 避免隔膜闭孔、热失控
- 大电芯（300Ah+）内部温度分布极不均匀，表面温度严重滞后

---

#### 🔥 C3.4.3 固态电池界面失效预警

| 属性 | 值 |
|-----|---|
| **算法类型**：原位EIS + 压力耦合 |
| **核心模型**：界面阻抗演化 + 失效预测 |
| **输入数据**：EIS谱图 + 压力数据 |
| **输出结果**：界面失效概率 |
| **电池类型复用** | ✅ 半固态/全固态专用 |
| **部署位置**：云端API |

**失效机制**：
```
固态电池主要死因：固-固界面接触失效
    ↓
监测指标:
  1. 界面阻抗Z_int（EIS提取）↑ → 接触不良
  2. 压力-容量滞后↑ → 呼吸效应异常
  3. 温度-阻抗解耦 → 局部过热点
    ↓
预警条件:
  IF Z_int增长速率 > threshold THEN
    → 界面剥离风险
  IF 压力突降 > threshold THEN
    → 机械失效
```

---

#### 🧪 C3.4.4 钠电自放电补偿

| 属性 | 值 |
|-----|---|
| **算法类型**：自放电观测器 |
| **核心模型**：高自放电率建模 + 容量修正 |
| **输入数据**：SOC-OCV偏差历史 |
| **输出结果**：修正后SOH |
| **电池类型复用** | ✅ 钠离子专用 |
| **部署位置**：云端API |

**钠离子特性**：
- 自放电率：5-8%/月（vs 锂电2-5%/月）
- 硬碳负极高比表面积 → 副反应多

**补偿算法**：
```
观测器:
  d(SOC_self_discharge)/dt = -k_sd(T) * SOC
    ↓
参数辨识:
  k_sd(T) = f(温度、荷电状态、循环次数)
    ↓
容量修正:
  SOH_corrected = SOH_measured + Capacity_loss_self_discharge
```

---

## L4 应用层级算法（Application Tier）

### A4.1 场景优化算法

#### 🚗 A4.1.1 电动汽车充电优化

| 属性 | 值 |
|-----|---|
| **算法类型**：多目标优化 |
| **核心模型**：MCC多级恒流 + 脉冲充电 |
| **输入数据**：电池状态、用户行程、电价 |
| **输出结果**：最优充电策略 |
| **优化目标**：充电时间、寿命衰减、用户满意度 |
| **电池类型复用** | ✅ 100%通用 |
| **部署位置**：车载BMS + 充电桩协同 |

**MCC多级恒流策略**：
```
基于析锂边界的动态电流调整:
  IF 析锂风险高:
    I_charge = 0.3C
  ELSE IF 析锂风险中:
    I_charge = 0.5C
  ELSE:
    I_charge = 0.7C (最大化充电速度)
    ↓
充电末端脉冲修复:
  负向脉冲消除浓差极化
  抑制SEI膜增厚
```

---

#### 🏠 A4.1.2 家庭储能优化

| 属性 | 值 |
|-----|---|
| **算法类型**：能量管理 |
| **核心模型**：电价预测 + 负载预测 |
| **输入数据**：光伏发电、负载、电价、电池状态 |
| **输出结果**：充放电策略 |
| **优化目标**：最小化电费、最大化自消纳率 |
| **电池类型复用** | ✅ 100%通用 |
| **部署位置**：家庭能源管理系统（HEMS） |

---

## L5 工商业层级算法（Industrial Tier）

### I5.1 能量管理算法

#### 🏭 I5.1.1 微网能量管理

| 属性 | 值 |
|-----|---|
| **算法类型**：混合整数线性规划（MILP） |
| **核心模型**：光储充检放一体化优化 |
| **输入数据**：光伏预测、负载预测、电价、电池状态 |
| **输出结果**：各单元功率分配 |
| **优化目标**：经济性、可靠性、碳排放 |
| **时间尺度**：日前优化 + 实时调整 |
| **电池类型复用** | ✅ 100%通用 |
| **部署位置**：微网能量管理系统（EMS） |

---

#### 🔋 I5.1.2 V2G双向优化

| 属性 | 值 |
|-----|---|
| **算法类型**：寿命损失补偿 |
| **核心模型**：V2G收益 - 寿命损失 |
| **输入数据**：电价、电池状态、用户行程 |
| **输出结果**：V2G参与策略 |
| **优化目标**：净收益最大化 |
| **电池类型复用** | ✅ 100%通用 |
| **部署位置**：V2G聚合平台 |

**寿命损失建模**：
```
V2G循环导致的容量损失:
  ΔQ_V2G = f(I_discharge, DOD, 温度, 循环次数)
    ↓
经济模型:
  净收益 = V2G收益 - 电池成本 × ΔQ_V2G / Q_total
```

---

### I5.2 资产管理算法

#### 💰 I5.2.1 储能电站资产评估

| 属性 | 值 |
|-----|---|
| **算法类型**：残值建模 |
| **核心模型**：RUL预测 + 市场价值评估 |
| **输入数据**：电池状态、历史数据、市场电价 |
| **输出结果**：资产残值、ABS证券化支持 |
| **应用场景**：资产交易、融资、保险 |
| **电池类型复用** | ✅ 100%通用 |
| **部署位置**：云端SaaS |

**残值评估模型**：
```
Residual_Value = Σ(Cash_Flow_t / (1+r)^t)
    ↓
Cash_Flow_t = (电价_arbitrage + 容量_services) × Capacity × SOH_t
    ↓
SOH_t = SOH_0 - f(RUL_prediction, degradation_rate)
```

---

#### ♻️ I5.2.2 电池回收决策

| 属性 | 值 |
|-----|---|
| **算法类型**：多准则决策 |
| **核心模型**：梯次利用筛选 + 报废推荐 |
| **输入数据**：SOH、RUL、故障历史、成本分析 |
| **输出结果**：梯次利用/报废/维修推荐 |
| **电池类型复用** | ✅ 100%通用 |
| **部署位置**：云端SaaS |

**决策树**：
```
IF SOH > 70% AND 无致命故障:
    → 梯次利用（储能/低速车）
ELSE IF SOH 40-70% AND 可修复:
    → 维修后梯次利用
ELSE:
    → 报废回收（材料提取）
```

---

## 算法复用性总结

### 第一性原理层 - 100%跨体系通用

| 算法类别 | 核心原理 | LFP | NCM | Na-ion | 半固态 | 全固态 |
|---------|---------|-----|-----|--------|-------|-------|
| **ECM等效电路** | Thevenin模型 | ✅ | ✅ | ✅ | ✅ | ✅ |
| **卡尔曼滤波** | 状态-参数估计 | ✅ | ✅ | ✅ | ✅ | ✅ |
| **ICA增量容量** | dQ/dV峰值 | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ |
| **EIS阻抗谱** | 界面阻抗 | ✅ | ✅ | ✅ | ✅ | ✅ |
| **热力学模型** | 焦耳热+熵热 | ✅ | ✅ | ✅ | ✅ | ✅ |
| **半物理ODE** | dQ/dN衰减 | ✅ | ✅ | ✅ | ✅ | ✅ |

⚠️ = 框架通用，峰值位置/参数需标定

### 体系特定参数 - 需针对标定

| 参数类型 | LFP | NCM | Na-ion | 固态 |
|---------|-----|-----|--------|------|
| **热失控起始温度** | ~500°C | ~200°C | 待标定 | 待标定 |
| **ICA峰值位置** | 3.35/3.45V | 3.65/3.80/3.95V | 待标定 | 待标定 |
| **自放电率** | 2-3%/月 | 3-5%/月 | 5-8%/月 | 1-2%/月 |
| **析锂边界** | Φanode<0V | Φanode<0V | N/A | N/A |

---

## 部署架构总结

```
┌─────────────────────────────────────────────────────────────┐
│  L1 生产层级：云端（批量分析）+ 边缘端（实时反馈）         │
├─────────────────────────────────────────────────────────────┤
│  L2 BMS层级：嵌入式C/C++库（ARM Cortex-M4/M7、RISC-V）     │
├─────────────────────────────────────────────────────────────┤
│  L3 云端层级：RESTful API + Docker容器 + SaaS平台          │
├─────────────────────────────────────────────────────────────┤
│  L4 应用层级：移动APP + Web控制台                          │
├─────────────────────────────────────────────────────────────┤
│  L5 工商业层级：企业级SaaS + 私有化部署                    │
└─────────────────────────────────────────────────────────────┘
```

---

**文档作者**：Claude Sonnet
**更新日期**：2026-02-08
**下次评审**：2026-03-15

---

# 附录：算法原理详细说明

> 本附录基于算法参考文件夹中的实际代码实现,详细说明各BAS Skill的核心算法原理、数学公式和实现细节。

## A. SOC估计算法

### A.1 安时积分法（Coulomb Counting）

**算法原理**：
```
SOC(k) = SOC(k-1) + I(k) × Δt / Qn / 3600
```

**参数说明**：
- `SOC(k)`：当前帧SOC（0-1之间的小数）
- `I(k)`：电流（A），充电为正，放电为负
- `Δt`：时间间隔（秒）
- `Qn`：额定容量（Ah）

**改进版本 - 累积误差修正**：
```python
def AnShiJiFenFa_linear(SOC_pre, I, delta_t, accumulated_amendment=0):
    """
    带累积误差修正的安时积分法

    核心思想：
    - 当SOC累积误差过大时，利用静置时间通过OCV校正
    - 使用滑动窗口限制单次修正幅度，避免跳变
    """
    yita = 1  # 充放电效率
    Qn = 280  # 初始容量
    max_amendment = 0.01  # 单次最大修正幅度

    amendment = yita * I * delta_t / Qn / 3600

    # 滑动窗口累积修正
    if accumulated_amendment >= max_amendment * 3:
        accumulated_amendment += amendment
        amendment = min(accumulated_amendment / 4, max_amendment)
    elif accumulated_amendment <= -3 * max_amendment:
        accumulated_amendment += amendment
        amendment = max(accumulated_amendment / 4, -max_amendment)

    SOC_new = SOC_pre - amendment

    # 边界处理
    if SOC_new > 1:
        accumulated_amendment += SOC_new - 1
        SOC_new = 1
    elif SOC_new < 0:
        accumulated_amendment += SOC_new
        SOC_new = 0

    return SOC_new, accumulated_amendment
```

**OCV-SOC插值**：
```python
def interpolation(x_, x, y):
    """
    线性插值函数
    x_: 待插值的OCV值
    x: OCV列表
    y: SOC列表
    """
    if x_ > x[0]:
        index = 1
        x1 = x[1]
    else:
        for index, x1 in enumerate(x):
            if x1 < x_:
                break
    x2 = x[index - 1]
    y1 = y[index]
    y2 = y[index - 1]

    result = y1 + (x_ - x1) * (y2 - y1) / (x2 - x1)
    return min(max(result, 0), 1.0)
```

---

### A.2 双自适应扩展卡尔曼滤波（DAEKF）

**算法类型**：状态-参数联合估计

**核心优势**：
- **双自适应**：同时估计SOC和模型参数（R0、R1、R2、C1、C2）
- **在线辨识**：实时跟踪电池内阻变化
- **Sage-Husa自适应**：动态调整过程噪声和观测噪声协方差

**数学模型**：

**状态方程**：
```
X(k) = [Q_loss, Uocv, U1, U2]^T

状态转移矩阵 A:
┌────────────────────────────────────────┐
│ 1,      0,                 0,       0  │
│ -Δuocv·u₀/Uocv²,         1,       0,  0  │
│ 0,      0,      exp(-Δt/τ₁),      0  │
│ 0,      0,                0,  exp(-Δt/τ₂)  │
└────────────────────────────────────────┘

控制矩阵 B:
┌──────┐
│  0   │
│  0   │
│ R₁(1-e^(-Δt/τ₁)) │
│ R₂(1-e^(-Δt/τ₂)) │
└──────┘

τ₁ = R₁·C₁, τ₂ = R₂·C₂
```

**观测方程**：
```
Y(k) = Uocv(k) - U₁(k) - U₂(k) - I(k)·R₀

观测矩阵 C = [0, 1, -1, -1]
```

**DAEKF核心算法**：
```python
def capacityAEKF(ik, vk, delta_uocv_soc, r0, r1, r2, c1, c2, dt,
                 qn=None, x0=None, p0=None,
                 mr0=None, mq0=None, u0=None,
                 xkpre=None, pkpre=None, k0=None,
                 b=None, iter_count=None, am=None, err_array=None,
                 calendar_degrad_index=None, imax=None):
    """
    双自适应扩展卡尔曼滤波 - 容量估计

    参数说明：
    - ik: 本帧电流（正电流是放电）
    - vk: 本帧电压
    - delta_uocv_soc: 当前SOC下的dOCV/dSOC梯度
    - r0, r1, r2, c1, c2: 电池内部参数
    - dt: 时间间隔（秒）

    内部状态（初始化时可省略）：
    - qn: 当前容量估计
    - x0: 状态向量 [Q_loss, Uocv, U1, U2]
    - p0: 误差协方差矩阵
    - mr0: 观测噪声协方差R
    - mq0: 过程噪声协方差Q
    """
    # 初始化
    if qn is None:
        imax = 0
        qn = 280  # 初始容量
        uocv = 3.2
        x0 = np.mat(np.zeros((4, 1)))
        x0[0, 0] = 0  # 容量损失
        x0[1, 0] = uocv
        p0 = np.mat(np.eye(4))

        mr0 = np.mat(np.array([1e-2]))  # 观测噪声协方差
        mq0 = np.mat(np.eye(4))  # 过程噪声协方差
        u0 = 0

        # Sage-Husa自适应参数
        b = 0.97
        iter_count = 1
        am = 100
        err_array = np.zeros(am)

        # 日历老化系数
        RUL = 4000
        calendar_degrad_perc = 0.2
        single_circle_calendar_degrad = (1 - 0.8) * calendar_degrad_perc / RUL
        circle_working_time = 7538 + 7174
        calendar_degrad_index = single_circle_calendar_degrad / circle_working_time

    # 更新最大电流（用于循环老化估计）
    if ik > imax:
        imax = ik
        if imax > 160:
            imax = 160
        cycle_0 = (160 - imax) * 70
        qn_0 = (1 - 0.95) / 700 * cycle_0

    # 计算时间常数
    tau1 = r1 * c1
    tau2 = r2 * c2
    e1 = math.exp(-dt / tau1)
    e2 = math.exp(-dt / tau2)

    # 状态转移矩阵
    ma = np.mat([[1, 0, 0, 0],
                 [-delta_uocv_soc * u0 / x0[1, 0] / x0[1, 0], 1, 0, 0],
                 [0, 0, e1, 0],
                 [0, 0, 0, e2]])

    # 控制矩阵
    mb = np.mat([[0], [0], [r1 * (1 - e1)], [r2 * (1 - e2)]])

    # 先验估计
    xkpre = ma * x0 + mb * u0
    ykpre = xkpre[1, 0] - xkpre[2, 0] - xkpre[3, 0] - ik * r0

    # 先验估计协方差
    pkpre = ma * p0 * ma.T + mq0

    # 观测矩阵
    ck = np.mat([[0, 1, -1, -1]])

    # 卡尔曼增益
    dot = ck * pkpre * ck.T + mr0
    inv = np.linalg.inv(dot)
    kk = pkpre * ck.T * inv

    # 后验估计
    verr = vk - ykpre
    xk = xkpre + kk * verr

    # 后验协方差
    pk = pkpre - kk * ck * pk

    # Sage-Husa自适应更新Q、R
    verr = vk - xk[1, 0] + xk[2, 0] + xk[3, 0] + ik * r0
    err_array[(iter_count - 1) % am] = verr * verr.T

    count = 0
    hk = 0
    for i in range(0, iter_count):
        if i == am:
            break
        hk += err_array[i]
        count += 1

    hk = hk / count
    mr0 = hk + ck * pk * ck.T
    mq0 = kk * hk * kk.T

    iter_count += 1
    p0 = pk
    x0 = xk
    u0 = ik

    # 容量衰减估计
    capacity_degradation = xk[0, 0]

    # 日历老化更新
    qn -= calendar_degrad_index * dt

    return (qn - np.abs(capacity_degradation)) / 280, qn, x0, p0, mr0, mq0, u0, b, iter_count, am, err_array, calendar_degrad_index, imax
```

**关键创新点**：
1. **日历老化建模**：分离循环老化和日历老化
   - 循环老化：与电流大小相关（大电流加速老化）
   - 日历老化：时间相关，与存储SOC、温度相关

2. **Sage-Husa自适应**：滑动窗口估计噪声统计特性
   - 窗口大小：100帧
   - 遗忘因子：b = 0.97

3. **双自适应**：同时估计容量损失和SOC

---

## B. 参数辨识算法

### B.1 RLS在线参数辨识（递推最小二乘）

**算法类型**：在线系统辨识

**核心优势**：
- **实时性**：每帧更新一次参数
- **遗忘因子**：适应电池参数缓慢变化
- **低计算量**：适合BMS嵌入式实现

**数学模型**：

**二阶RC等效电路差分方程**：
```
U(k) = k₁·U(k-1) + k₂·U(k-2) + k₃·I(k) + k₄·I(k-1) + k₅·I(k-2)
```

**RLS递推公式**：
```python
def ffrls(uk_array, ik_array, delta_t, lam=None, p0=None, theta0=None):
    """
    遗忘因子递推最小二乘法（FFRLS）

    参数说明：
    - uk_array: [u(k-2), u(k-1), u(k)] 电压序列
    - ik_array: [i(k-2), i(k-1), i(k)] 电流序列
    - delta_t: 采样间隔
    - lam: 遗忘因子（初始化时输入1，以后输入上次输出值）
    - p0: 误差协方差矩阵
    - theta0: 参数向量

    输出：
    - r0, r1, r2: 直流内阻、交流内阻1、交流内阻2
    - c1, c2: 电容1、电容2
    - lam, p0, theta0: 内部状态（下次调用时传入）
    """
    # 初始化
    if lam is None:
        lam = 1
        p0 = 1e15 * np.eye(6)
        theta0 = [[1.60348982e+00],
                  [-6.11157514e-01],
                  [2.43065751e-02],
                  [-3.64824006e-04],
                  [5.58584104e-04],
                  [-2.00459665e-04]]

    # 构造回归向量
    phi = np.array([[uk_array[1], uk_array[0], 1,
                     ik_array[2], ik_array[1], ik_array[0]]])  # 1×6
    phit = phi.T  # 6×1

    yk = uk_array[2]

    # 更新增益矩阵
    inv = np.linalg.inv(phi @ p0 @ phit + lam)
    kk = p0 @ phit @ inv  # 6×1

    # 更新误差协方差矩阵
    pk = (np.eye(6) - kk @ phi) @ p0 / lam

    # 更新参数向量
    err_yk = yk - phi @ theta0
    thetak = theta0 + kk * err_yk

    # 保存状态
    p0 = pk
    theta0 = thetak

    # 从差分方程参数提取R、C参数
    k1 = thetak[0, 0]
    k2 = thetak[1, 0]
    k3 = -thetak[3, 0]
    k4 = -thetak[4, 0]
    k5 = -thetak[5, 0]

    uocv = thetak[2, 0] / (1 - k1 - k2)

    dt2 = delta_t ** 2
    k0 = dt2 / (1 - k1 - k2)

    a = -k2 * k0
    b = k0 * (k1 + 2 * k2) / delta_t
    c = k0 * (k3 + k4 + k5) / dt2
    d = -k0 * (k4 + 2 * k5) / delta_t

    # 求解时间常数 τ₁ = R₁·C₁, τ₂ = R₂·C₂
    b4a = b * b - 4 * a
    b4a_sqrt = cmath.sqrt(b4a)
    ba1 = (b + b4a_sqrt) / 2
    ba2 = (b - b4a_sqrt) / 2

    tau1 = min(ba1, ba2)
    tau2 = max(ba1, ba2)

    # 计算R、C参数
    r0 = -k5 / k2
    r2 = (tau2 * c + r0 * tau1 - d) / (tau2 - tau1)
    r1 = c - r2 - r0
    c1 = tau1 / r1
    c2 = tau2 / r2

    return np.abs(r0.real), np.abs(r1.real), np.abs(r2.real), np.abs(c1.real), np.abs(c2.real), lam, p0, theta0
```

**关键参数**：
- **遗忘因子λ**：通常取0.95-1.0
  - λ = 1：标准RLS（适用于时不变系统）
  - λ < 1：遗忘因子RLS（适用于时变系统）
- **初始协方差P₀**：通常取1e10~1e15·I（大数值保证初期的快速收敛）

**适用场景**：
- 实时跟踪电池内阻变化
- SOC/SOH估计的参数自适应
- BMS嵌入式实现（计算量小）

---

### B.2 PSO离线参数辨识（粒子群优化）

**算法类型**：元启发式全局优化

**核心优势**：
- **全局搜索**：避免陷入局部最优
- **无需梯度**：适用于非线性、非凸优化问题
- **并行性**：粒子并行评估，适合多核加速

**数学模型**：

**目标函数**：
```
f = Σ |Y(k+1) - U*(k+1)|²

其中：
Y(k+1) = Uocv(k+1) - R₀·I(k) - U₁(k+1) - U₂(k+1)
U₁(k+1) = exp(-Δt/R₁C₁)·U₁(k) + R₁·(1-exp(-Δt/R₁C₁))·I(k)
U₂(k+1) = exp(-Δt/R₂C₂)·U₂(k) + R₂·(1-exp(-Δt/R₂C₂))·I(k)
```

**PSO算法流程**：
```python
# 伪代码
def PSO_parameter_identification(HPPC_data):
    """
    基于HPPC测试数据的PSO参数辨识

    参数：
    - HPPC_data: 包含电流、电压、时间序列

    步骤：
    1. R₀辨识：通过电流突变时的电压降
       R₀ = [(U_A-U_B) + (U_C-U_D)] / (2·I)

    2. PSO优化R₁、R₂、C₁、C₂
    """
    # Step 1: R₀辨识
    A = V[current_start]      # 电流突变前电压
    B = V[current_start + 8]  # 电流突变后电压
    C = V[current_end - 5]    # 电流恢复前电压
    D = V[current_end + 8]    # 电流恢复后电压
    R0 = (A - B + C - D) / (2 * I_pulse)

    # Step 2: PSO初始化
    SearchAgents_no = 30  # 粒子数量
    Max_iter = 10         # 迭代次数

    # 参数搜索空间
    lb = [1e-06, 1e-06, 1e+01, 1e+01]  # [R1_min, R2_min, C1_min, C2_min]
    ub = [5e-02, 3e-02, 1e+08, 1e+08]  # [R1_max, R2_max, C1_max, C2_max]
    dim = 4  # 维度

    # PSO参数
    w = 0.8   # 惯性权重
    c1 = 2    # 个体学习因子
    c2 = 2    # 社会学习因子

    # Step 3: PSO主循环
    for iter in range(Max_iter):
        for i in range(SearchAgents_no):
            # 评估适应度
            fitness = objective_function(particles[i], HPPC_data)

            # 更新个体最优
            if fitness < pbest_fitness[i]:
                pbest[i] = particles[i].copy()
                pbest_fitness[i] = fitness

            # 更新全局最优
            if fitness < gbest_fitness:
                gbest = particles[i].copy()
                gbest_fitness = fitness

        # 更新粒子位置和速度
        for i in range(SearchAgents_no):
            r1, r2 = np.random.rand(2)
            velocity[i] = (w * velocity[i] +
                          c1 * r1 * (pbest[i] - particles[i]) +
                          c2 * r2 * (gbest - particles[i]))
            particles[i] += velocity[i]

    return gbest  # 最优参数 [R1, R2, C1, C2]
```

**适用场景**：
- 离线参数标定（实验室HPPC测试）
- 新电池型号的参数库建立
- 模型验证与校准

---

## C. SOH估计算法

### C.1 ICA（增量容量分析）

**算法类型**：电化学特征提取

**核心原理**：
```
ICA = dQ/dV = (dQ/dt) / (dV/dt) = I / (dV/dt)
```

**实现步骤**：

**Step 1: 数据预处理**
```python
# 读取充电数据
df = pd.read_csv('charge_data.csv')
df['Q'] = df['SOC'] * 280  # 容量（Ah）

# 构建V-Q曲线
plt.plot(df['Q'], df['电压(V)'])
```

**Step 2: 计算dV/dQ**
```python
dvdq = []
v0, q0 = df.iloc[0]['电压(V)'], df.iloc[0]['Q']

for index, row in df.iterrows():
    v, q = row['电压(V)'], row['Q']
    try:
        result = (v - v0) / (q - q0)
    except:
        result = (v - v0) / 0.0035  # 避免除零

    # 异常值过滤
    if q > 25 and (result > 0.05 or result < -0.001):
        result = result0

    dvdq.append(result)
    v0, q0 = v, q
    result0 = result

df['dv/dq'] = dvdq
```

**Step 3: 低通滤波**
```python
# 一阶低通滤波器
# Y(k+1) = α·X(k+1) + (1-α)·Y(k)
dvdq_filted0 = dvdq[0]
alpha = 0.008  # 滤波系数
dvdq_filted = []

for index, value in enumerate(dvdq):
    dvdq_filted0 = value * alpha + (1 - alpha) * dvdq_filted0
    dvdq_filted.append(dvdq_filted0)

df['dv/dq_filted'] = dvdq_filted
```

**Step 4: 五重高斯分布拟合**
```python
from scipy.optimize import curve_fit

# 五重高斯分布函数
def gaussian(x, *param):
    """
    param[0-4]: 高度 h1, h2, h3, h4, h5
    param[5-9]: 位置 μ1, μ2, μ3, μ4, μ5
    param[10-14]: 宽度 σ1, σ2, σ3, σ4, σ5
    """
    result = 0
    for i in range(5):
        h = param[i]
        mu = param[5 + i]
        sigma = param[10 + i]
        result += h * np.exp(-np.power(x - mu, 2.) / (2 * np.power(sigma, 2.)))
    return result

# 参数初值和边界
param0 = [0.0003, 0.0009, 0.0009, 0.0015, 0.002,  # 高度
          220, 180, 85, 65, 60,                      # 位置
          10, 10, 5, 2, 2]                           # 宽度

param_bounds = (
    [0, 0, 0.00025, 0.001, 0.001,   # 高度下限
     200, 150, 75, 65, 40,           # 位置下限
     0.1, 0.1, 0.1, 0.1, 0.1],       # 宽度下限
    [0.001, 0.002, 0.002, 0.0025, 0.004,  # 高度上限
     250, 200, 100, 80, 60,               # 位置上限
     15, 15, 10, 10, 10]                  # 宽度上限
)

# 曲线拟合
param, pcov = curve_fit(gaussian, x, y, p0=param0,
                        bounds=param_bounds, maxfev=500)

# 提取峰特征
position = [param[5], param[6], param[7], param[8], param[9]]
height = [param[0], param[1], param[2], param[3], param[4]]
width = [param[10], param[11], param[12], param[13], param[14]]
```

**Step 5: 特征工程（19个特征）**
```python
features = {
    # 峰位置
    'peak1_pos': position[0],
    'peak2_pos': position[1],
    'peak3_pos': position[2],
    'peak4_pos': position[3],
    'peak5_pos': position[4],

    # 峰高度
    'peak1_height': height[0],
    'peak2_height': height[1],
    'peak3_height': height[2],
    'peak4_height': height[3],
    'peak5_height': height[4],

    # 峰宽度
    'peak1_width': width[0],
    'peak2_width': width[1],
    'peak3_width': width[2],
    'peak4_width': width[3],
    'peak5_width': width[4],

    # 峰间距
    '12_distance': position[0] - position[1],
    '23_distance': position[1] - position[2],
    '34_distance': position[2] - position[3],
    '45_distance': position[3] - position[4],
}
```

**老化模式识别**：
```
NCM三元锂峰值位置：
  Peak 1 (~3.65V): Stage IV → III
  Peak 2 (~3.80V): Stage III → II  ⭐ 主峰
  Peak 3 (~3.95V): Stage II → I

老化模式：
  - 主峰左移 >50mV → 析锂（锂沉积）
  - 峰值高度下降 → LLI（活性锂损失）
  - 峰值面积减小 → LAM（活性物质损失）
  - 低电位异常峰 → 严重析锂
```

---

### C.2 SOH初始值猜测（基于时间）

**算法类型**：经验模型

**应用场景**：新电池启动时的SOH初始化

```python
def soh_first_guess(start_year, start_month=6, over_quantity=False):
    """
    基于启动时长猜测SOH初始值

    老化模型：
    - 第一年：4%
    - 后续每年：3%

    等价于：
    - 前12月：每月1/3%
    - 13-100月：每月1/4%
    - 100月后：每月2/5%
    """
    import datetime
    now = datetime.datetime.now()
    current_year = now.year
    current_month = now.month

    month_duration = (current_year - start_year) * 12 + (current_month - start_month)

    soh_droped = 0
    for i in range(month_duration):
        if i < 12:
            soh_droped += 0.01 / 3
        elif i < 100:
            soh_droped += 0.01 / 4
        else:
            soh_droped += 0.02 / 5

    soh0 = 1.05 if over_quantity else 1.0
    soh_pre = (1 - soh_droped) * soh0

    return soh_pre
```

---

## D. 故障诊断算法

### D.1 析锂检测 - 弛豫电压分析法

**算法类型**：时域分析 + 模式识别

**核心原理**：
充电结束后的弛豫阶段（电流为0），正常电芯和析锂电芯的电压恢复曲线不同。

**实现步骤**：

**Step 1: 提取弛豫电压曲线**
```python
# 提取充电结束后的静置段电压
start = 4115  # 充电结束点
end = 4700    # 静置结束点
v_list = np.array(df.loc[start:end].v)

# 计算一阶导数（dv/dt）
dv = np.gradient(v_list)

# 低通滤波
from scipy.signal import butter, filtfilt
cutoff = 0.1  # 截止频率
nyquist = 2
order = 1
b, a = butter(order, cutoff / nyquist, btype='low')
filtered_dv = filtfilt(b, a, dv)

# 计算二阶导数（ddv/dt²）
ddv = np.gradient(filtered_dv)
```

**Step 2: 析锂判断**
```python
# 未发生析锂：二阶导数大部分大于0
# 发生析锂：二阶导数有连续负值区域

ddv_min = np.min(ddv[:60])
ddv_min_index = np.argmin(ddv[:60])

# 寻找ddv最小值右边的最大值
ddv_right = ddv[ddv_min_index:]
ddv_max = np.max(ddv_right)
ddv_max_index = np.argmax(ddv_right)

# 判断是否有连续负值
negative_count = np.sum(ddv < 0)
if negative_count > 50:  # 阈值：50秒
    plating_detected = True
else:
    plating_detected = False
```

**Step 3: 特征提取**
```python
if plating_detected:
    # 特征1：最小值与最大值之间的时间间距
    feature1 = ddv_max_index

    # 特征2：dv曲线析锂峰值高度
    # 找到ddv=0的点（dv曲线的峰值）
    for idx, val in enumerate(ddv[ddv_min_index:ddv_min_index+ddv_max_index]):
        if val >= 0 and ddv[idx-1] < 0:
            break
    dv_plating_peak = filtered_dv[ddv_min_index + idx]
    feature2 = filtered_dv[-1] - dv_plating_peak
```

**物理意义**：
- 析锂导致负极表面镀锂，改变界面动力学
- 弛豫阶段，镀锂的再嵌入过程导致电压恢复曲线异常
- 二阶导数的负值区域反映析锂的严重程度

---

### D.2 香农熵故障检测

**算法类型**：信息论 + 统计分析

**核心原理**：
通过EMD（经验模态分解）提取电压残差，计算香农熵评估系统有序度。

**实现步骤**：

**Step 1: EMD分解**
```python
from PyEMD.EMD import EMD

num_of_batteries = 10
origin_data = []
for i in range(num_of_batteries):
    s = np.random.random(100)  # 模拟100秒的电压值
    origin_data.append(s)

# 执行EMD分解
residue_afer_EMD = []
for i in range(num_of_batteries):
    emd = EMD()
    IMF = emd.emd(origin_data[i])
    residue_afer_EMD.append(IMF[-1])  # 提取残差

residue_afer_EMD = np.array(residue_afer_EMD).T  # (100, 10)
```

**Step 2: Min-Max归一化**
```python
MW_len = 15  # 滑动窗口长度
residue_MW = residue_afer_EMD[:MW_len, :]

V_matrix = np.zeros_like(residue_MW)
for i in range(V_matrix.shape[0]):
    for j in range(V_matrix.shape[1]):
        xmin = np.min(residue_MW[:, j])
        xmax = np.max(residue_MW[:, j])
        V_matrix[i][j] = (residue_MW[i][j] - xmin) / (xmax - xmin)
```

**Step 3: 计算概率矩阵P**
```python
P_matrix = np.zeros_like(V_matrix)
for i in range(P_matrix.shape[0]):
    for j in range(P_matrix.shape[1]):
        P_matrix[i][j] = V_matrix[i][j] / np.sum(V_matrix[:, j])
```

**Step 4: 计算香农熵**
```python
dj_list = np.zeros(P_matrix.shape[0])
for j in range(P_matrix.shape[0]):
    ej = 0
    for i in range(P_matrix.shape[1]):
        if P_matrix[j][i] != 0:
            ej += P_matrix[j][i] * np.log(P_matrix[j][i])
    ej = ej * (-1) / np.log(P_matrix.shape[1])
    dj_list[j] = 1 - ej  # 冗余度
```

**Step 5: 计算权重W**
```python
Wj_list = np.zeros_like(dj_list)
for j in range(len(Wj_list)):
    Wj_list[j] = dj_list[j] / np.sum(dj_list)
```

**Step 6: 基于香农熵权重的评分**
```python
Si_list = np.zeros(P_matrix.shape[1])
for i in range(P_matrix.shape[1]):
    Si_list[i] = np.sum(np.multiply(residue_MW[:, i], Wj_list))
```

**Step 7: 改进Z-分数**
```python
Si_max = np.max(Si_list)
S_bar = np.sum(Si_list - Si_max) / (len(Si_list) - 1)
Sigma_S = np.sqrt(np.sum(np.power((Si_list - S_bar), 2)) / (len(Si_list) - 1))
Zsi_list = (Si_list - S_bar) / Sigma_S

# 故障判断
risk_indices = np.where(Zsi_list > 3)[0]  # 阈值：3
```

**关键创新**：
- **改进Z-分数**：`S_bar = Σ(Si - Smax) / (n-1)`（排除最大值，避免离群点干扰）
- **滑动窗口**：MW=15，平衡灵敏度和计算量
- **EMD分解**：提取低频趋势，去除高频噪声

---

## E. RUL预测算法

### E.1 非时序RUL预测（特征工程）

**算法类型**：监督学习 + 特征工程

**核心思想**：从充放电曲线提取统计特征，训练机器学习模型预测RUL。

**特征工程（27个特征）**：

**电流特征（9个）**：
```python
def extract_current_features(df):
    data = np.array(df['电流(A)'])
    features = []

    # 统计特征
    features += [
        data.max(),        # I_max
        data.min(),        # I_min
        np.median(data),   # I_median
        data.mean(),       # I_mean
        data.std(),        # I_std
        st.skew(data),     # I_skew（偏度）
        st.kurtosis(data)  # I_kurtosis（峰度）
    ]

    # 平台值特征
    bin_num = 100
    cut, cut_values = pd.cut(data, bins=bin_num,
                             labels=list(range(bin_num)),
                             retbins=True)
    n, bins, patches = plt.hist(cut, bins=bin_num)

    # 找平台值（前3个最多的区间）
    delta_n = n[1:] - n[:-1]
    index_list = []
    n_list = []
    for index, value in enumerate(delta_n):
        if index == 0:
            continue
        if value < 0 and delta_n[index - 1] > 0:
            index_list.append(index)
            n_list.append(n[index])

    # 选择前3个
    index_list = np.array(index_list)[
        getListMaxNumIndex(n_list, topk=3)
    ]

    # 提取平台值位置和宽度
    for cut_value in cut_values[index_list]:
        p1, p2 = 0, len(data)
        up_down_lim = (0.3, -0.2)  # 电流平台容差

        for index, value in enumerate(data):
            if value >= cut_value + up_down_lim[0]:
                p1 = index
            if value <= cut_value + up_down_lim[1]:
                p2 = index
                break

        features += [cut_value, (p2 - p1) * delta_t]

    return features  # 9个特征
```

**电压特征（9个）**：
```python
def extract_voltage_features(df):
    data = np.array(df['电压(V)'])
    features = []

    # 统计特征
    features += [
        data.max(),
        data.min(),
        np.median(data),
        data.mean(),
        data.std(),
        st.skew(data),
        st.kurtosis(data)
    ]

    # 平台值特征（类似电流）
    # ...

    return features  # 9个特征
```

**总特征（27个）**：
```python
# 电流特征（9个）
features = extract_current_features(df)

# 电压特征（9个）
features += extract_voltage_features(df)

# 循环次数标签
features.append(cycle_number)

# 特征列表
col = [
    'I_max', 'I_min', 'I_median', 'I_mean', 'I_std', 'I_skew', 'I_kurto',
    'I_plat1_loc', 'I_plat1_wid', 'I_plat2_loc', 'I_plat2_wid',
    'I_plat3_loc', 'I_plat3_wid',
    'V_max', 'V_min', 'V_median', 'V_mean', 'V_std', 'V_skew', 'V_kurto',
    'V_plat1_loc', 'V_plat1_wid', 'V_plat2_loc', 'V_plat2_wid',
    'V_plat3_loc', 'V_plat3_wid',
    'label'  # RUL标签
]
```

**模型训练**：
```python
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
import joblib

# 准备数据
dataset = np.array(feature_df)[:, :-1]  # 特征
label_set = np.array(feature_df)[:, -1]  # 标签

# 划分训练集、测试集
X_train, X_test, y_train, y_test = train_test_split(
    dataset, label_set, test_size=0.3, random_state=0
)

# 训练模型
model = GradientBoostingRegressor(n_estimators=100)
model.fit(X_train, y_train)

# 评估
score = model.score(X_test, y_test)
print(f"R² Score: {score}")

# 保存模型
joblib.dump(model, 'rul_gbr.pkl')
```

**模型对比**：
| 模型 | R² Score | 优点 | 缺点 |
|------|----------|------|------|
| LinearRegression | 0.85 | 简单快速 | 欠拟合 |
| RandomForest | 0.92 | 鲁棒性强 | 过拟合风险 |
| GradientBoosting | 0.94 | 精度高 | 训练慢 |
| MLP | 0.91 | 非线性拟合 | 需调参 |

---

### E.2 CNN-LSTM时序RUL预测

**算法类型**：深度学习 + 时序建模

**网络架构**：
```python
class CNN_LSTM(nn.Module):
    def __init__(self, args):
        super(CNN_LSTM, self).__init__()

        # 1D CNN层（特征提取）
        self.conv = nn.Sequential(
            nn.Conv1d(in_channels=args.in_channels,
                     out_channels=args.hidden_channels,
                     kernel_size=3),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=3, stride=1),

            nn.Conv1d(in_channels=args.hidden_channels,
                     out_channels=args.hidden_channels,
                     kernel_size=3),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=3, stride=1),

            # ... 更多卷积层
        )

        # LSTM层（时序建模）
        self.lstm = nn.LSTM(
            input_size=args.out_channels,
            hidden_size=args.hidden_size,
            num_layers=args.num_layers,
            batch_first=True
        )

        # 全连接层（输出）
        self.fc = nn.Linear(args.hidden_size, args.output_size)

    def forward(self, x):
        # 输入: (batch_size, seq_len, input_size)
        x = x.permute(0, 2, 1)  # → (batch_size, input_size, seq_len)
        x = self.conv(x)        # CNN特征提取
        x = x.permute(0, 2, 1)  # → (batch_size, seq_len, hidden)
        x, _ = self.lstm(x)     # LSTM时序建模
        x = self.fc(x)          # 全连接输出
        x = x[:, -1, :]         # 取最后时刻
        return x
```

**数据预处理**：
```python
# 滑动窗口构建时序样本
# 输入: (batch_size, time_step, feature_nums)
# time_step: 时间窗口长度
# feature_nums: 传感器数量（电压、电流、温度等）

# 示例
time_step = 24
feature_nums = 7  # V, I, T, SOC, SOH, ...
```

**训练配置**：
```python
# 超参数
args = {
    'in_channels': 7,       # 输入特征数
    'hidden_channels': 32,  # CNN隐藏通道数
    'out_channels': 32,     # CNN输出通道数
    'hidden_size': 128,     # LSTM隐藏层大小
    'num_layers': 2,        # LSTM层数
    'output_size': 1        # 输出（RUL）
}

# 训练参数
learning_rate = 0.00001
EPOCH = 100000
```

---

## F. EIS谱图分析

### F.1 EIS数据处理

**算法类型**：阻抗谱拟合

**核心原理**：通过EIS Nyquist图提取电池内部参数。

**实现步骤**：

**Step 1: 划分高低频**
```python
# 斜率法（比频率经验法更鲁棒）
deri = []
Zreal0, Zimag_neg0 = EIS_df.iloc[0]['Zreal'], EIS_df.iloc[0]['Zimag_neg']

for i in range(1, len(EIS_df)):
    Zreal, Zimag_neg = EIS_df.iloc[i]['Zreal'], EIS_df.iloc[i]['Zimag_neg']
    dZi = (Zimag_neg - Zimag_neg0) / (Zreal - Zreal0)
    Zreal0, Zimag_neg0 = Zreal, Zimag_neg
    deri.append(dZi)

deri = [deri[0]] + deri
EIS_df['dZi'] = deri

# 找拐点（斜率从负变正）
v0 = deri[0]
guaidian = []
for i, value in enumerate(deri):
    if v0 < 0 and value > 0:
        guaidian.append(i)
    v0 = value

EIS_high = EIS_df[EIS_df.index < guaidian[0]]    # 高频部分
EIS_low = EIS_df[EIS_df.index >= guaidian[0]]    # 低频部分
```

**Step 2: 霍夫变换确定圆心**
```python
def calc_abc_from_line_2d(x0, y0, x1, y1):
    """计算直线方程 ax + by + c = 0 的系数"""
    a = y0 - y1
    b = x1 - x0
    c = x0 * y1 - x1 * y0
    return a, b, c

def get_line_cross_point(line1, line2):
    """计算两条直线的交点"""
    a0, b0, c0 = calc_abc_from_line_2d(*line1)
    a1, b1, c1 = calc_abc_from_line_2d(*line2)
    D = a0 * b1 - a1 * b0
    if D == 0:
        return None
    x = (b0 * c1 - b1 * c0) / D
    y = (a1 * c0 - a0 * c1) / D
    return x, y

# 蒙特卡洛法求圆心
start = 30  # 起始点（避开最高频的噪声）
a_list, b_list = [], []

for i in range(start + 1, len(EIS_high)):
    if i % 1 != 0:
        continue
    Zreal, Zimag_neg = EIS_df.iloc[i]['Zreal'], EIS_df.iloc[i]['Zimag_neg']

    # 以点为圆心，以半圆为半径
    theta = np.linspace(0, 2 * np.pi, 100)
    radius = r  # 半径

    a = radius * np.cos(theta) + Zreal
    b = radius * np.sin(theta) + Zimag_neg

    a_list += list(a)
    b_list += list(b)

# 2D直方图找最高频点（圆心）
frequency, x_, y_, _ = plt.hist2d(a_list, b_list,
                                     (len(EIS_high), len(EIS_high)),
                                     cmap=plt.cm.jet)
fm = frequency.max()
index = np.unravel_index(frequency.argmax(), frequency.shape)
center = x_[index[0]], y_[index[1]]
```

**Step 3: 等效电路拟合**
```python
from impedance.models.circuits import CustomCircuit

# 定义等效电路模型
# Rs: 溶液电阻
# R1: 电荷转移电阻
# CPE1: 常相位元件（双电层）
# R2: 扩散电阻
# CPE2: Warburg元件
circuit_string = 'Rs-R1-CPE1-R2-CPE2'

# 初始化电路
circuit = CustomCircuit(circuit_string, initial_guess=[
    0.01,  # Rs (Ω)
    0.01,  # R1 (Ω)
    0.001, # CPE1 Q
    0.9,   # CPE1 alpha
    0.01,  # R2 (Ω)
    0.001, # CPE2 Q
    0.8    # CPE2 alpha
])

# 拟合
circuit.fit(frequencies, Z)

# 提取参数
Rs, R1, Q1, alpha1, R2, Q2, alpha2 = circuit.parameters_

print(f"Rs = {Rs:.4f} Ω")
print(f"Rct = {R1:.4f} Ω")
print(f"CPE = {Q1:.4e}, alpha = {alpha1:.2f}")
```

**物理意义**：
- **Rs（溶液电阻）**：电解液阻抗、接触阻抗
- **Rct（电荷转移电阻）**：电化学反应阻抗
  - Rct ↑ → SEI膜增厚、界面退化
- **CPE（常相位元件）**：双电层电容的非理想性
  - alpha < 1 → 表面粗糙度、孔隙分布
- **Warburg（扩散阻抗）**：锂离子扩散阻抗
  - Warburg系数 ↑ → 扩散受阻（析锂、活性物质损失）

---

## G. 算法选择指南

### G.1 SOC估计

| 场景 | 推荐算法 | 理由 |
|------|---------|------|
| BMS嵌入式 | DAEKF | 精度高、鲁棒性强、可在线辨识参数 |
| 云端分析 | 安时积分 + OCV修正 | 简单可靠、有静置时间时精度高 |
| 钠离子电池 | 分段滤波 | 适应硬碳负极的OCV特性 |

### G.2 SOH估计

| 场景 | 推荐算法 | 理由 |
|------|---------|------|
| 在线估计 | ICA片段（10%充电区间） | 无需完整充电曲线、实时更新 |
| 离线分析 | XGBoost + 特征工程 | 精度高（≤1.5%）、鲁棒性强 |
| RUL预测 | 半物理ODE模型 | 物理意义明确、小样本即可、跨体系通用 |

### G.3 参数辨识

| 场景 | 推荐算法 | 理由 |
|------|---------|------|
| 在线跟踪 | RLS（遗忘因子） | 实时性好、计算量小、适合BMS |
| 离线标定 | PSO | 全局搜索、避免局部最优、无需梯度 |

### G.4 故障诊断

| 场景 | 推荐算法 | 理由 |
|------|---------|------|
| 析锂检测 | 弛豫电压分析法 | 充电结束即可判断、无需额外传感器 |
| 内短路检测 | SOS基因图谱 | 漏电流<10mA、提前2个月预警 |
| 异常检测 | 香农熵 + 改进Z-分数 | 抗噪性强、自动故障分级 |
| 热失控预警 | MEMS气体传感器阵列 | 提前2-5分钟、比温控更早 |

### G.5 RUL预测

| 场景 | 推荐算法 | 理由 |
|------|---------|------|
| 小数据 | 半物理ODE模型 | 物理约束、泛化能力强 |
| 大数据 | CNN-LSTM | 自动特征提取、时序建模 |
| 快速预测 | 非时序特征工程 + GBR | 特征明确、训练快 |

---

## H. 算法实现注意事项

### H.1 数值稳定性

**问题**：卡尔曼滤波中的矩阵求逆可能数值不稳定

**解决方案**：
```python
# 使用QR分解替代直接求逆
# inv = np.linalg.inv(dot)  # 不推荐
Q, R = np.linalg.qr(dot)  # 推荐
inv = np.linalg.solve(R, Q.T)
```

### H.2 边界条件处理

**问题**：SOC超出[0, 1]范围

**解决方案**：
```python
# 饱和函数
def saturate(x, lower, upper):
    return np.clip(x, lower, upper)

SOC = saturate(SOC, 0.0, 1.0)
```

### H.3 初始值敏感性

**问题**：PSO、RLS等算法对初始值敏感

**解决方案**：
```python
# 多次初始化，取最优
def pso_multi_init(func, n_init=5):
    best_fitness = np.inf
    best_x = None

    for i in range(n_init):
        x, fitness = PSO(func)
        if fitness < best_fitness:
            best_fitness = fitness
            best_x = x

    return best_x, best_fitness
```

### H.4 数据质量

**问题**：异常数据、噪声、缺失值

**解决方案**：
```python
# 中值滤波去噪
from scipy.signal import medfilt
filtered_data = medfilt(raw_data, kernel_size=5)

# 线性插值补缺失值
df['voltage'] = df['voltage'].interpolate(method='linear')

# 异常值剔除（3σ原则）
mean = np.mean(data)
std = np.std(data)
data_clean = data[np.abs(data - mean) < 3 * std]
```

---

**文档作者**：Claude Sonnet
**更新日期**：2026-02-08
**下次评审**：2026-03-15
