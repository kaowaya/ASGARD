// reference/algo-theory.md
# EKF SOC估计算法理论

## 1. 等效电路模型 (ECM)
本算法基于**双极化（2RC）等效电路模型**进行状态估计。

该模型包含：
- 一个电压源 $U_{ocv}$ (开路电压)
- 一个欧姆内阻 $R_0$
- 两个 RC 极化网络 ($R_1//C_1$ 和 $R_2//C_2$)，分别描述电池内部快速极化和慢速扩散过程。

电池端电压 $U_t$的方程表示为：
$$U_t = U_{ocv}(SOC) - I \cdot R_0 - U_{p1} - U_{p2}$$

其中 $U_{p1}$ 和 $U_{p2}$是两个 RC 并在环路上的压降，其动态特性微分方程如下：
$$\dot{U}_{p1} = -\frac{U_{p1}}{R_1 C_1} + \frac{I}{C_1}$$
$$\dot{U}_{p2} = -\frac{U_{p2}}{R_2 C_2} + \frac{I}{C_2}$$

## 2. 状态空间方程的离散化
为了在单片机中计算，我们选取状态向量 $x = [U_{p1}, U_{p2}, SOC]^T$，输入 $u = I$，进行零阶保持离散化。

**离散状态方程**:
$$x_{k+1} = A x_k + B u_k + w_k$$

其中系统矩阵表示为：
$$
A = \begin{bmatrix}
e^{-\Delta t/\tau_1} & 0 & 0 \\
0 & e^{-\Delta t/\tau_2} & 0 \\
0 & 0 & 1
\end{bmatrix}
$$
其中 $\tau_1 = R_1 C_1$, $\tau_2 = R_2 C_2$

输入矩阵：
$$
B = \begin{bmatrix}
R_1 (1 - e^{-\Delta t/\tau_1}) \\
R_2 (1 - e^{-\Delta t/\tau_2}) \\
-\frac{\Delta t}{Q_n \times 3600}
\end{bmatrix}
$$
*(注：公式中假设充电电流$I$为负。若约定充电为正，B矩阵第三项需取正号)*

**离散观测方程**:
$$y_k = h(x_k, u_k) + v_k$$
$$y_k = U_{ocv}(SOC_k) - U_{p1,k} - U_{p2,k} - I_k R_0$$

## 3. 扩展卡尔曼滤波 (EKF)
由于观测方程中 $U_{ocv}(SOC)$ 是非线性的，我们需要对观测方程在当前工作点求雅可比矩阵(Jacobian Matrix) $H_k$：

$$H_k = \frac{\partial h}{\partial x} \Big|_{x = \hat{x}_{k|k-1}} = \begin{bmatrix} -1 & -1 & \frac{d U_{ocv}}{d SOC} \end{bmatrix}$$

EKF五个递推步骤为：
1. **状态预测**: $\hat{x}_{k|k-1} = A \hat{x}_{k-1} + B u_{k-1}$
2. **协方差预测**: $P_{k|k-1} = A P_{k-1} A^T + Q$
3. **计算卡尔曼增益**: $K_k = P_{k|k-1} H_k^T (H_k P_{k|k-1} H_k^T + R)^{-1}$
4. **状态更新**: $\hat{x}_k = \hat{x}_{k|k-1} + K_k (y_k - \hat{y}_{k|k-1})$
5. **协方差更新**: $P_k = (I - K_k H_k) P_{k|k-1}$

*($Q$ 是状态过程噪声协方差矩阵，代表模型的置信度；$R$ 是观测噪声协方差矩阵，代表传感器测量的置信度。)*
