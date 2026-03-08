// templates/cpp/soc_ukf_core.h
#ifndef SOC_UKF_CORE_H
#define SOC_UKF_CORE_H

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

// 状态维数 N = 3 (U_p1, U_p2, SOC)
// Sigma点个数 = 2N + 1 = 7
#define UKF_N 3
#define UKF_SIGMA_COUNT 7

// UKF状态结构体 (基于3阶状态向量的非线性估计)
typedef struct {
    double x[UKF_N];           // 状态: [U_p1, U_p2, SOC]
    double P[UKF_N * UKF_N];   // 协方差矩阵P (3x3拉平)
    
    int is_initialized;
} UKF_State;

// 电池等效电路常数与 UKF 超参数
typedef struct {
    double Qn;      
    double R0;      
    double R1;      
    double R2;      
    double C1;      
    double C2;      
    
    double dt;      
    
    // UT 变换参数
    double alpha;
    double beta;
    double kappa;
    
    // 固定的系统与观测噪声
    double Q[UKF_N * UKF_N]; 
    double R; 
} UKF_Params;

/**
 * @brief Cholesky 分解 (求矩阵的主平方根 L, L*L^T = A)
 * 工业级要求包含了异常容错(防御除0与对角为负)
 * @param A 输入正定对称矩阵指针
 * @param n 矩阵维度
 * @param L 输出下三角矩阵指针
 * @return int 成功返回1，失败(非正定)返回0
 */
int cholesky_decomposition(const double* A, int n, double* L);

/**
 * @brief UKF SOC核心算法步进函数 (1D数组与静态内存解法)
 * 直接使用预先计算好的Sigma点进行Sigma传播，彻底抛弃雅可比矩阵
 * 
 * @param ik 电流输入 (充电为负，放电为正)
 * @param vk 电压输入 (V)
 * @param params 常量参数指针
 * @param state 跨周期持久化状态指针
 * @return double 返回本次UKF最优重构的SOC (0.0~1.0)
 */
double run_soc_ukf_step(double ik, double vk, const UKF_Params* params, UKF_State* state);

#ifdef __cplusplus
}
#endif

#endif // SOC_UKF_CORE_H
