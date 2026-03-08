// templates/cpp/soc_coulomb_counting.h
#ifndef SOC_COULOMB_COUNTING_H
#define SOC_COULOMB_COUNTING_H

#include <stdint.h>
// 针对不支持数学库的极低端MCU，我们可以自己实现宏替换
#ifndef fmaxf
#define fmaxf(a,b) (((a)>(b))?(a):(b))
#endif
#ifndef fminf
#define fminf(a,b) (((a)<(b))?(a):(b))
#endif

#ifdef __cplusplus
extern "C" {
#endif

// 安时积分法内部状态结构体，用于断电持久化
typedef struct {
    float soc;             // 核心状态：当前SOC (0.0f ~ 1.0f)
    uint32_t last_time_ms; // 上一次更新的时间戳
    int is_initialized;    // 是否已经完成初值设定
} CoulombCounting_State;

// 电池物理参数配置
typedef struct {
    float capacity_Ah;     // 电池额定容量(Ah)
    float current_deadband;// 电流死区阈值(A)，低于此值认为电流为0
} CoulombCounting_Config;

/**
 * @brief 库伦效率计算 (基于温度)
 * 
 * @param current_A 瞬时电流
 * @param temperature_C 电池温度
 * @return float 库伦效率 (0~1.0)
 */
static inline float calculate_coulombic_efficiency(float current_A, float temperature_C) {
    // 简化模型：充电为负(吸收)，放电为正(输出)
    if (current_A <= 0.0f) {  // 充电过程，库伦效率接近100%
        return 1.0f;
    } else {      // 放电过程，根据温度稍微打折
        float T_ref = 25.0f;
        float alpha = 0.005f;
        // 比如在 -20度 时，效率大约是 0.99 * (1 - 0.005*(1 - (-20)/25)) = 0.99 * 0.986 = 0.976
        float eta = 0.99f * (1.0f - alpha * (1.0f - temperature_C / T_ref));
        // 限制边界
        return fmaxf(0.8f, fminf(1.0f, eta)); 
    }
}

/**
 * @brief 执行单步安时积分状态更新
 * 
 * @param config 参数配置参数
 * @param state 算法状态(会被更新)
 * @param current_A 当前电流(A)，约定：充电为负，放电为正
 * @param temperature_C 当前温度(°C)
 * @param timestamp_ms 毫秒级时间戳，必须单向递增
 */
static inline void run_coulomb_counting_step(const CoulombCounting_Config* config, 
                                            CoulombCounting_State* state, 
                                            float current_A, 
                                            float temperature_C, 
                                            uint32_t timestamp_ms) {
    if (!state->is_initialized) {
        state->last_time_ms = timestamp_ms;
        state->is_initialized = 1;
        return; // 第一帧只记录时间
    }

    // 1. 防呆死区处理（过滤传感器噪声）
    if (current_A > -config->current_deadband && current_A < config->current_deadband) {
        current_A = 0.0f;
    }

    // 2. 时间解析
    uint32_t dt_ms = timestamp_ms - state->last_time_ms;
    state->last_time_ms = timestamp_ms;
    
    // 如果发生时间回环或异常大跨度（如系统重启但是内存还在），跳过积分
    if (dt_ms == 0 || dt_ms > 3600000) { 
        return; 
    }
    
    // 转换为小时
    float dt_h = (float)dt_ms / 3600000.0f;

    // 3. 计算放电过程的库伦效率损耗
    float eta = calculate_coulombic_efficiency(current_A, temperature_C);

    // 4. 安时积分方程
    // dSOC = -(eta * I * dt) / Capacity
    // 【约定】：因为这里定义充电为负(-I)，dSOC将为正(+)，SOC增加。
    // 如果定义放电为正(+I)，dSOC将为负(-)，SOC减小。
    float dSOC = -(eta * current_A * dt_h) / config->capacity_Ah;
    
    state->soc += dSOC;

    // 5. 极端鲁棒性限幅控制 (Clamp to 0~1)
    state->soc = fmaxf(0.0f, fminf(1.0f, state->soc));
}

#ifdef __cplusplus
}
#endif

#endif // SOC_COULOMB_COUNTING_H
