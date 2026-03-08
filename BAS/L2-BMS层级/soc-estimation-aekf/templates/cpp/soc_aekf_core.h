// templates/cpp/soc_aekf_core.h
#ifndef SOC_AEKF_CORE_H
#define SOC_AEKF_CORE_H

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

// AEKF状态结构体 (包含Q和R矩阵以便持久化跨周期记忆)
typedef struct {
    double x[4];    // 状态量: [dummy, U_p1, U_p2, SOC]
    double P[16];   // 误差协方差矩阵 (拉平为1D数组，4x4)
    double Q[16];   // 过程噪声协方差自适应估计 (4x4)
    double R;       // 观测噪声方差自适应估计 (标量，因为只有一个测量y=电压)
    
    int is_initialized;
    uint32_t step_count; // Sage-Husa递推计步器 (k)
} AEKF_State;

// 电池模型参数设计
typedef struct {
    double Qn;      // 额定容量(Ah)
    double R0;      // 欧姆内阻
    double R1;      // 极化内阻1
    double R2;      // 极化内阻2
    double C1;      // 极化电容1
    double C2;      // 极化电容2
    
    double dt;      // 采样间隔(s)
    
    // AEKF 特有参数
    double forget_factor_b;  // Sage-Husa 遗忘因子 (如 0.97)
    double R_min, R_max;     // R发散限制
} AEKF_Params;

/**
 * @brief AEKF SOC核心算法步进函数 (1D数组内存展开版，无动态分配)
 * 这个函数实现了Sage-Husa估计器以自适应更新Q和R。
 * 
 * 限制：因为C不自带矩阵库，工业级交付往往由专门的底层数学加速库计算。
 * 这里的声明要求传入拉平的数组供目标平台的数学库调用。
 * 
 * @param ik 电流输入 (充电为负，放电为正)
 * @param vk 电压输入 (V)
 * @param params 常数模型参数指针
 * @param state 跨周期的持久化状态指针
 * @return double 返回本次迭代最新的SOC (0.0~1.0)
 */
double run_soc_aekf_step(double ik, double vk, const AEKF_Params* params, AEKF_State* state);

#ifdef __cplusplus
}
#endif

#endif // SOC_AEKF_CORE_H
