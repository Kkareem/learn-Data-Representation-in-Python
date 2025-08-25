import numpy as np
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
matplotlib.use("QtAgg")

np.random.seed(12345)
df = pd.DataFrame([np.random.normal(32000,200000,3650), 
                   np.random.normal(43000,100000,3650), 
                   np.random.normal(43500,140000,3650), 
                   np.random.normal(48000,70000,3650)], 
                  index=[1992,1993,1994,1995])

# Set your y value of interest:
v = 42000  # change this

years = df.index.to_numpy()
means = df.mean(axis=1).to_numpy()
stds = df.std(axis=1, ddof=1).to_numpy()
n = df.shape[1]
se = stds / np.sqrt(n)
ci95 = 1.96 * se
lower = means - ci95
upper = means + ci95

colors = []
for lo, up in zip(lower, upper):
    if up < v:
        colors.append('tab:blue')
    elif lo > v:
        colors.append('tab:red')
    else:
        colors.append('white')

fig, ax = plt.subplots(figsize=(8, 5))
x = np.arange(len(years))
ax.bar(x, means, yerr=ci95, capsize=6, edgecolor='black', linewidth=1.0, color=colors)
ax.set_xticks(x, years)
ax.set_ylabel("Mean value (with 95% CI)")
ax.set_title("Easiest Option — 3-Color CI Classification")
ax.axhline(v, linestyle='--', linewidth=1.2)

from matplotlib.patches import Patch
legend_elems = [Patch(facecolor='tab:blue', edgecolor='black', label='Below v (CI entirely below)'),
                Patch(facecolor='white', edgecolor='black', label='Contains v (v inside CI)'),
                Patch(facecolor='tab:red', edgecolor='black', label='Above v (CI entirely above)')]
ax.legend(handles=legend_elems, loc='upper left', frameon=True)

plt.tight_layout()
plt.show()
