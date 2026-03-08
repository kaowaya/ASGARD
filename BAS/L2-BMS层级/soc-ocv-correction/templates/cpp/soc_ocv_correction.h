// templates/cpp/soc_ocv_correction.h
#ifndef SOC_OCV_CORRECTION_H
#define SOC_OCV_CORRECTION_H

#include <stdint.h>
#include <math.h>

#ifndef fmaxf
#define fmaxf(a,b) (((a)>(b))?(a):(b))
#endif
#ifndef fminf
#define fminf(a,b) (((a)<(b))?(a):(b))
#endif

#ifdef __cplusplus
extern "C" {
#endif

#define OCV_TABLE_SIZE 11

// 内置LFP电池的基础OCV放电态查找表（25°C），实际工程应包含多维查表
static const float default_ocv_table_x[OCV_TABLE_SIZE] = {2.50f, 3.10f, 3.20f, 3.25f, 3.28f, 3.29f, 3.30f, 3.32f, 3.35f, 3.40f, 3.50f};
static const float default_ocv_table_y[OCV_TABLE_SIZE] = {0.00f, 0.05f, 0.10f, 0.20f, 0.40f, 0.50f, 0.60f, 0.80f, 0.90f, 0.98f, 1.00f};

// OCV查表修正法内部状态结构体，保存于EEPROM
typedef struct {
    float soc_real;             // 真实内部SOC (包含突变)
    float soc_disp;             // 平滑后的显示SOC 
    uint32_t last_time_ms;      // 上一次循环时间戳
    uint32_t rest_timer_ms;     // 电池已经静置的累积时间
    float last_rest_voltage;    // 上一次静置电压（用于计算 dV/dt 进行弛豫判定）
    int is_initialized;
} OcvCorrection_State;

// 算法配置
typedef struct {
    float capacity_Ah;           // 额定容量
    float current_deadband;      // 电流死区
    uint32_t rest_time_threshold_ms; // 要求的静置时间阈值(如2小时=7200000)
    float max_jump_step;         // 单次循环允许SOC_disp跳变的最大步长（如 0.0001f /100ms）
} OcvCorrection_Config;

/**
 * @brief 线性插值查表得到SOC
 */
static inline float lookup_soc_by_ocv(float ocv) {
    if (ocv <= default_ocv_table_x[0]) return default_ocv_table_y[0];
    if (ocv >= default_ocv_table_x[OCV_TABLE_SIZE-1]) return default_ocv_table_y[OCV_TABLE_SIZE-1];

    for (int i = 0; i < OCV_TABLE_SIZE - 1; i++) {
        if (ocv >= default_ocv_table_x[i] && ocv <= default_ocv_table_x[i+1]) {
            float ratio = (ocv - default_ocv_table_x[i]) / (default_ocv_table_x[i+1] - default_ocv_table_x[i]);
            return default_ocv_table_y[i] + ratio * (default_ocv_table_y[i+1] - default_ocv_table_y[i]);
        }
    }
    return 0.5f; // Fallback
}

/**
 * @brief 库伦效率计算 
 */
static inline float calculate_eta(float current_A, float temp_C) {
    if (current_A <= 0.0f) return 1.0f; // 充电
    float eta = 0.99f * (1.0f - 0.005f * (1.0f - temp_C / 25.0f)); // 放电
    return fmaxf(0.8f, fminf(1.0f, eta));
}

/**
 * @brief 执行单步OCV查表修正算法
 * 
 * @param is_corrected 输出标志变量：如果发生修正则置1
 */
static inline void run_ocv_correction_step(const OcvCorrection_Config* config, 
                                          OcvCorrection_State* state, 
                                          float current_A, 
                                          float voltage_V,
                                          float temperature_C, 
                                          uint32_t timestamp_ms,
                                          int* is_corrected) {
    *is_corrected = 0; // 默认未修正
    
    if (!state->is_initialized) {
        state->last_time_ms = timestamp_ms;
        state->is_initialized = 1;
        // 冷启动第一次直接强信电压做初始SOC
        state->soc_real = lookup_soc_by_ocv(voltage_V);
        state->soc_disp = state->soc_real;
        return; 
    }

    uint32_t dt_ms = timestamp_ms - state->last_time_ms;
    state->last_time_ms = timestamp_ms;
    if (dt_ms == 0 || dt_ms > 3600000) return; 

    // 判断电流是否在死亡期，更新静置计时器
    if (current_A > -config->current_deadband && current_A < config->current_deadband) {
        current_A = 0.0f;
        state->rest_timer_ms += dt_ms;
    } else {
        state->rest_timer_ms = 0; // 电流一出现，打断静置
    }

    // --- 安时积分步骤 ---
    float dt_h = (float)dt_ms / 3600000.0f;
    float eta = calculate_eta(current_A, temperature_C);
    
    float dSOC = -(eta * current_A * dt_h) / config->capacity_Ah;
    state->soc_real += dSOC;
    state->soc_real = fmaxf(0.0f, fminf(1.0f, state->soc_real));

    // --- OCV 修正步骤 ---
    // 条件：静置时间大于阈值（如2小时）
    if (state->rest_timer_ms > config->rest_time_threshold_ms) {
        // 取得弛豫后电压反推的精确SOC
        float mapped_soc = lookup_soc_by_ocv(voltage_V);
        
        // 只有当偏差超过1%才修正，避免频繁微调
        if (fabsf(state->soc_real - mapped_soc) > 0.01f) {
            state->soc_real = mapped_soc;
            *is_corrected = 1;
        }
    }

    // --- 无跳变平滑释放层 (Display layer) ---
    // SOC_disp 向 SOC_real 逼近，但受限最大步长
    // 而且包含防呆：如果正在放电(dSOC<0)，显示SOC绝不能升高
    float soc_diff = state->soc_real - state->soc_disp;
    
    if (soc_diff > 0.0f) {
        float step = fminf(config->max_jump_step, soc_diff);
        // 如果放电中，即使 real_soc 高了，也不要立刻补回去，防止反物理的“电量越开越多”
        if (current_A > 0.0f) {
            step = 0.0f; // 禁止上涨
        }
        state->soc_disp += step;
    } else if (soc_diff < 0.0f) {
        float step = fminf(config->max_jump_step, -soc_diff);
        // 充电中，禁止下降
        if (current_A < 0.0f) {
            step = 0.0f; 
        }
        state->soc_disp -= step;
    }

    // 最后再叠加本周期的dSOC (安时积分的基础累加)，以及限域
    state->soc_disp += (current_A != 0.0f) ? dSOC : 0.0f;
    state->soc_disp = fmaxf(0.0f, fminf(1.0f, state->soc_disp));
}

#ifdef __cplusplus
}
#endif

#endif // SOC_OCV_CORRECTION_H
