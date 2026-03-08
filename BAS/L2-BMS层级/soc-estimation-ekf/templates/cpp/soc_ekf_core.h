// templates/cpp/soc_ekf_core.h
#ifndef SOC_EKF_CORE_H
#define SOC_EKF_CORE_H

#ifdef __cplusplus
extern "C" {
#endif

// EKF 状态结构体
typedef struct {
    double x[4];    // 状态量: [dummy, U_p1, U_p2, SOC]
    double P[16];   // 误差协方差矩阵 (拉平为1D数组)
    int is_initialized;
} EKF_State;

// 电池参数结构体
typedef struct {
    double Qn;      // 额定容量(Ah)
    double R0;      // 欧姆内阻
    double R1;      // 极化内阻1
    double R2;      // 极化内阻2
    double C1;      // 极化电容1
    double C2;      // 极化电容2
    double dt;      // 采样间隔(s)
} Battery_Params;

/**
 * @brief EKF SOC核心算法步进函数 (此为示例头文件申明)
 * 
 * @param ik 电流输入 (充电负，放电正 - 依据项目约定调整)
 * @param vk 电压输入 (V)
 * @param tk 温度输入 (℃，暂留接口)
 * @param params 电池固有参数指针
 * @param state 算法内部状态量指针(需在外部持久化)
 * @return double 返回计算得到的SOC (0.0~1.0)
 */
double run_soc_ekf_step(double ik, double vk, double tk, const Battery_Params* params, EKF_State* state);

#ifdef __cplusplus
}
#endif

#endif // SOC_EKF_CORE_H
