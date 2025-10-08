import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# ---------- 图与拉普拉斯 ----------
def laplacian(W: np.ndarray) -> np.ndarray:
    D = np.diag(W.sum(axis=1))
    return D - W

def ring_graph(n: int, w: float = 1.0) -> np.ndarray:
    """无向环形图邻接矩阵"""
    A = np.zeros((n, n), float)
    for i in range(n):
        A[i, (i - 1) % n] = w
        A[i, (i + 1) % n] = w
    return A

# ---------- 本地输入 u_i(t) 及其导数 ----------
def u_vec(t: float, n: int) -> np.ndarray:
    # 你可以按需要改成任意可导信号
    # 不同频率/相位的正弦
    u = np.empty(n)
    for i in range(n):
        w = 0.6 + 0.1 * i
        phi = 0.3 * i
        u[i] = np.sin(w * t + phi)
    return u

def udot_vec(t: float, n: int) -> np.ndarray:
    du = np.empty(n)
    for i in range(n):
        w = 0.6 + 0.1 * i
        phi = 0.3 * i
        du[i] = w * np.cos(w * t + phi)
    return du

# ---------- DAC 动力学 ----------
def rhs_dac(t, y, A, B, alpha):
    """
    y = [x (n), q (n)]
    dot q = - L_B x
    dot x = - alpha (x - u) - L_A x + L_B^T q + udot
    """
    n = A.shape[0]
    x = y[:n]
    q = y[n:]

    L_A = laplacian(A)
    L_B = laplacian(B)

    u = u_vec(t, n)
    ud = udot_vec(t, n)

    dq = - L_B @ x
    dx = - alpha * (x - u) - L_A @ x + (L_B.T @ q) + ud
    return np.concatenate([dx, dq])

# ---------- 主程序 ----------
def main():
    np.set_printoptions(precision=4, suppress=True)

    # 网络与参数
    n = 6
    A = ring_graph(n, w=1.0)     # 普通一致性矩阵
    B = A.copy()                 # 积分一致性矩阵（常用 A=B）
    alpha = 1.2                  # 本地跟踪增益

    # 初值（任意都可；实践上常设 x(0)=u(0), q(0)=0 以减少过渡）
    x0 = u_vec(0.0, n)           # 或者：np.random.randn(n)
    q0 = np.zeros(n)             # 或者：np.random.randn(n) 也完全可行
    y0 = np.concatenate([x0, q0])

    # 数值积分
    t_span = (0.0, 40.0)
    t_eval = np.linspace(*t_span, 1200)
    sol = solve_ivp(rhs_dac, t_span, y0, t_eval=t_eval,
                    args=(A, B, alpha),
                    rtol=1e-7, atol=1e-9, dense_output=False)

    t = sol.t
    Y = sol.y
    x_traj = Y[:n, :]                  # 每行对应一个代理的 x_i(t)
    q_traj = Y[n:, :]

    # 计算真实平均 以及 误差
    u_bar = np.array([u_vec(tt, n).mean() for tt in t])
    x_bar = x_traj.mean(axis=0)
    track_err = x_bar - u_bar          # 应该指数收敛到 0（速率 ~ alpha）

    # ---------- 画图 ----------
    plt.figure(figsize=(10, 6))
    for i in range(n):
        plt.plot(t, x_traj[i, :], lw=1.0, label=f"$x_{i+1}(t)$" if i < 6 else None)
    plt.plot(t, u_bar, lw=2.0, linestyle="--", label=r"$\bar{u}(t)$")
    plt.title("Dynamic Average Consensus: states tracking the time-varying average")
    plt.xlabel("t")
    plt.ylabel("value")
    plt.legend(ncol=3, fontsize=9)
    plt.grid(True, alpha=0.3)

    plt.figure(figsize=(8, 3.4))
    plt.plot(t, track_err, lw=2.0)
    plt.title(r"Tracking error of the average:  $\bar x(t)-\bar u(t)$")
    plt.xlabel("t")
    plt.ylabel("error")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()