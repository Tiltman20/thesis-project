import numpy as np
import matplotlib.pyplot as plt

def cauchy(x, x0=0, gamma=1):
    return (1 / np.pi) * (gamma / ((x - x0)**2 + gamma**2))

x = np.linspace(-10, 10, 1000)
y = cauchy(x, x0=0, gamma=1)

plt.figure(figsize=(10, 6))

plt.plot(x, cauchy(x, 0, 0.5), label="γ=0.5", color=(207/255,24/255,32/255))
plt.plot(x, cauchy(x, 0, 1), label="γ=1", color=(236/255,101/255,37/255))
plt.plot(x, cauchy(x, 0, 2), label="γ=2", color=(175/255,54/255,140/255))

plt.xlabel("x", fontsize=12)
plt.ylabel("f(x)", fontsize=12)
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()

plt.gca().set_facecolor("#f5f5f5")

plt.axhline(0, linewidth=1)
plt.axvline(0, linewidth=1)

plt.show()