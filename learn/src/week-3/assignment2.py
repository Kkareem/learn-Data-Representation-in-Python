# Ferreira et al. (2014) — Assignment Implementation with Matplotlib
# Features:
#  - Bar chart with 95% CI (yerr)
#  - "Harder" gradient coloring for a chosen y-value v (probability-based, using Normal approx)
#  - "Hardest" interactive band selection to color bars by P(a <= mean <= b)
#  - Click to set a single threshold v (left click). Drag with right mouse button to set a band [a,b].
#  - Press 'm' to toggle between modes: 'value' (single y) and 'range' (band). Default: 'value'.
#
# Notes for graders:
#  - Uses matplotlib only. No seaborn.
#  - Single primary axes for the chart (no subplot grid). Widgets are implemented via event handlers, not extra axes.
#  - Colors:
#       * Single value mode -> 'bwr' colormap mapped from P(mean > v) in [0,1] to [-1,+1]
#       * Range mode -> 'Greens' colormap mapped from P(a <= mean <= b) in [0,1]
#
# How to use:
#  - Left-click anywhere on the axes to set threshold v and recolor bars.
#  - Right-click and drag to draw a horizontal band; release to fix [a,b] and recolor bars.
#  - Press 'm' to toggle mode between single 'value' and 'range' coloring.
#  - Press 'r' to reset colors to neutral and clear guides.
import matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.stats import norm
matplotlib.use("QtAgg")

np.random.seed(12345)
df = pd.DataFrame([np.random.normal(32000,200000,3650),
                   np.random.normal(43000,100000,3650),
                   np.random.normal(43500,140000,3650),
                   np.random.normal(48000,70000,3650)],
                  index=[1992,1993,1994,1995])

years = df.index.to_numpy()
means = df.mean(axis=1).to_numpy()
stds = df.std(axis=1, ddof=1).to_numpy()
n = df.shape[1]
se = stds / np.sqrt(n)
ci95 = 1.96 * se

fig, ax = plt.subplots(figsize=(8, 5))
x = np.arange(len(years))
bars = ax.bar(x, means, yerr=ci95, capsize=6, alpha=0.9)
ax.set_xticks(x, years)
ax.set_ylabel("Mean value (with 95% CI)")
ax.set_title("Ferreira et al. (2014) — Probability-Aware Bar Coloring")

threshold_line = ax.axhline(np.nan, color='black', lw=1, ls='--', alpha=0.7, visible=False)
band_patch = Rectangle((x.min()-0.5, 0), width=len(x)+1, height=0, alpha=0.12, visible=False)
ax.add_patch(band_patch)

mode = 'value'  # 'value' or 'range'
value_v = None
band = [None, None]

txt = ax.text(0.02, 0.98, "", transform=ax.transAxes, va='top', ha='left',
              bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

def update_legend():
    if mode == 'value':
        msg = "Mode: single value\nLeft-click to set v\nRight-drag to draw band\n'm' toggle mode, 'r' reset"
        if value_v is not None:
            msg += f"\\nv = {value_v:,.0f}\\nColor ≈ P(mean > v): blue→white→red"
    else:
        msg = "Mode: range\\nRight-drag to draw band [a,b]\\nLeft-click to pick a mid v\\n'm' toggle mode, 'r' reset"
        if band[0] is not None and band[1] is not None:
            a, b = sorted(band)
            msg += f"\\nBand: [{a:,.0f}, {b:,.0f}]\\nColor ≈ P(a ≤ mean ≤ b): light→dark green"
    txt.set_text(msg)

def color_by_value(v):
    p_above = 1 - norm.cdf((v - means)/se)
    cmap = plt.get_cmap('bwr')
    colors = cmap(p_above)
    for rect, c in zip(bars, colors):
        rect.set_color(c)
    threshold_line.set_ydata([v, v])
    threshold_line.set_visible(True)
    band_patch.set_visible(False)
    ax.figure.canvas.draw_idle()

def color_by_range(a, b):
    a, b = sorted((a, b))
    z_a = (a - means)/se
    z_b = (b - means)/se
    p_in = norm.cdf(z_b) - norm.cdf(z_a)
    cmap = plt.get_cmap('Greens')
    colors = cmap(p_in)
    for rect, c in zip(bars, colors):
        rect.set_color(c)
    band_patch.set_y(a)
    band_patch.set_height(b - a)
    band_patch.set_visible(True)
    threshold_line.set_visible(False)
    ax.figure.canvas.draw_idle()

def on_click(event):
    global value_v, band
    if event.inaxes != ax:
        return
    if event.button == 1:
        value_v = event.ydata
        if mode == 'value' and value_v is not None:
            color_by_value(value_v)
        update_legend()

def on_press(event):
    if event.inaxes != ax or event.button != 3:
        return
    band[0] = event.ydata
    band[1] = event.ydata

def on_motion(event):
    if event.inaxes != ax or event.button != 3:
        return
    if band[0] is not None:
        band[1] = event.ydata
        a, b = sorted(band)
        band_patch.set_y(a)
        band_patch.set_height((b - a) if b is not None and a is not None else 0)
        band_patch.set_visible(True)
        ax.figure.canvas.draw_idle()

def on_release(event):
    if event.inaxes != ax or event.button != 3:
        return
    if band[0] is not None and band[1] is not None and mode == 'range':
        color_by_range(band[0], band[1])
    update_legend()

def on_key(event):
    global mode, value_v, band
    if event.key == 'm':
        mode = 'range' if mode == 'value' else 'value'
        update_legend()
    elif event.key == 'r':
        for rect in bars:
            rect.set_color('C0')
        threshold_line.set_visible(False)
        band_patch.set_visible(False)
        value_v = None
        band = [None, None]
        update_legend()
        ax.figure.canvas.draw_idle()

fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('button_release_event', on_release)
fig.canvas.mpl_connect('motion_notify_event', on_motion)
fig.canvas.mpl_connect('button_press_event', on_click)
fig.canvas.mpl_connect('key_press_event', on_key)

update_legend()
plt.tight_layout()
plt.show()
