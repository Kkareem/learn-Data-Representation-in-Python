# %matplotlib widget   # uncomment if you have ipympl installed
import matplotlib
matplotlib.use("QtAgg")
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.widgets import Slider

rng = np.random.default_rng(42)

# --- Figure & layout (2x2 plots + a row of sliders) ---
plt.close('all')
fig = plt.figure(figsize=(10, 7), constrained_layout=True)
gs = gridspec.GridSpec(3, 2, figure=fig, height_ratios=[1, 1, 0.42])

ax_norm = fig.add_subplot(gs[0, 0])
ax_gamma = fig.add_subplot(gs[0, 1])
ax_exp  = fig.add_subplot(gs[1, 0])
ax_unif = fig.add_subplot(gs[1, 1])

# Sliders live in a simple grid of Axes in the bottom row
slider_axes = []
for i in range(6):
    # create small axes evenly spaced across the bottom row
    # using normalized figure coords for flexible placement
    left = 0.05 + (i % 3) * 0.31
    bottom = 0.06 if i < 3 else 0.01
    slider_axes.append(fig.add_axes([left, bottom, 0.28, 0.03]))

# --- Slider definitions (initial values mirror the prompt) ---
# Normal(mu, sigma)
s_mu   = Slider(slider_axes[0], r'Normal μ',   valmin=-5.0, valmax=1.0,  valinit=-2.5, valstep=0.1)
s_sig  = Slider(slider_axes[1], r'Normal σ',   valmin=0.2,  valmax=3.0,  valinit=1.0,  valstep=0.1)

# Gamma(k, θ)
s_k    = Slider(slider_axes[2], r'Gamma k',    valmin=0.5,  valmax=8.0,  valinit=2.0,  valstep=0.1)
s_theta= Slider(slider_axes[3], r'Gamma θ',    valmin=0.2,  valmax=3.0,  valinit=1.5,  valstep=0.1)

# Exponential(λ) + shift
s_lambda = Slider(slider_axes[4], r'Exp λ',    valmin=0.2,  valmax=2.0,  valinit=0.5,  valstep=0.05)  # λ = 1/scale
s_shift  = Slider(slider_axes[5], r'Exp shift',valmin=4.0,  valmax=10.0, valinit=7.0,  valstep=0.5)

# Sample size slider (place it above others if you prefer)
ax_n = fig.add_axes([0.70, 0.915, 0.28, 0.04])
s_n  = Slider(ax_n, 'Samples / frame', valmin=100, valmax=1000, valinit=400, valstep=10)

# --- Axis configuration & shared styling ---
for ax in (ax_norm, ax_gamma, ax_exp, ax_unif):
    ax.set_ylim(0, 0.6)
    ax.grid(True, alpha=0.25)
    ax.set_ylabel("Density")

ax_norm.set_title("x1: Normal")
ax_gamma.set_title("x2: Gamma")
ax_exp.set_title("x3: Exponential + shift")
ax_unif.set_title("x4: Uniform")

# Reasonable, shared x-limits so panels line up (based on the guide in the prompt)
ax_norm.set_xlim(-7, 3)
ax_gamma.set_xlim(-1, 12)
ax_exp.set_xlim(4, 14)
ax_unif.set_xlim(12, 22)

# Fixed bins per panel for visual stability across frames
bins_norm = np.linspace(-7, 3, 21)
bins_gamma = np.linspace(-1, 12, 26)
bins_exp = np.linspace(4, 14, 21)
bins_unif = np.linspace(12, 22, 21)

# Placeholders for artists so we can efficiently redraw
hist_artists = {
    'norm': None, 'gamma': None, 'exp': None, 'unif': None
}

# Helper to (re)draw a density histogram and return the artists
def draw_hist(ax, data, bins):
    ax.cla()  # clear axes to keep patch count stable/easy
    ax.grid(True, alpha=0.25)
    # density=True to normalize like your guide
    n, _, patches = ax.hist(data, bins=bins, density=True, alpha=0.6)
    return patches

# Initialize with first frame so axes titles/limits persist
def init():
    n = int(s_n.val)
    # Draw one batch using the current slider params
    x_norm = rng.normal(loc=s_mu.val, scale=s_sig.val, size=n)
    x_gamma = rng.gamma(shape=s_k.val, scale=s_theta.val, size=n)
    x_exp = rng.exponential(scale=1.0/s_lambda.val, size=n) + s_shift.val
    x_unif = rng.uniform(low=14.0, high=20.0, size=n)

    # Redraw each panel
    draw_hist(ax_norm, x_norm, bins_norm)
    ax_norm.set_title("x1: Normal")
    ax_norm.set_xlim(-7, 3); ax_norm.set_ylim(0, 0.6)

    draw_hist(ax_gamma, x_gamma, bins_gamma)
    ax_gamma.set_title("x2: Gamma")
    ax_gamma.set_xlim(-1, 12); ax_gamma.set_ylim(0, 0.6)

    draw_hist(ax_exp, x_exp, bins_exp)
    ax_exp.set_title("x3: Exponential + shift")
    ax_exp.set_xlim(4, 14); ax_exp.set_ylim(0, 0.6)

    draw_hist(ax_unif, x_unif, bins_unif)
    ax_unif.set_title("x4: Uniform [14, 20]")
    ax_unif.set_xlim(12, 22); ax_unif.set_ylim(0, 0.6)

    # Text labels roughly like the guide
    ax_norm.text(s_mu.val - 1.5, 0.5, 'x1\nNormal')
    ax_gamma.text(np.mean(x_gamma) - 1.5, 0.5, 'x2\nGamma')
    ax_exp.text(np.mean(x_exp) - 1.5, 0.5, 'x3\nExponential')
    ax_unif.text(15.0, 0.5, 'x4\nUniform')

    return []

# Animation update: fresh samples every frame (keeps it lively)
def update(frame):
    n = int(s_n.val)

    # Sample with current slider parameters
    x_norm = rng.normal(loc=s_mu.val, scale=s_sig.val, size=n)
    x_gamma = rng.gamma(shape=s_k.val, scale=s_theta.val, size=n)
    x_exp = rng.exponential(scale=1.0/s_lambda.val, size=n) + s_shift.val
    # Keep uniform strictly controlled by its canonical bounds (as in the guide)
    x_unif = rng.uniform(low=14.0, high=20.0, size=n)

    # Redraw each panel, preserve titles/limits
    ax_norm.cla(); ax_norm.grid(True, alpha=0.25)
    ax_norm.hist(x_norm, bins=bins_norm, density=True, alpha=0.6)
    ax_norm.set_title("x1: Normal"); ax_norm.set_xlim(-7, 3); ax_norm.set_ylim(0, 0.6)
    ax_norm.text(s_mu.val - 1.5, 0.5, 'x1\nNormal')

    ax_gamma.cla(); ax_gamma.grid(True, alpha=0.25)
    ax_gamma.hist(x_gamma, bins=bins_gamma, density=True, alpha=0.6)
    ax_gamma.set_title("x2: Gamma"); ax_gamma.set_xlim(-1, 12); ax_gamma.set_ylim(0, 0.6)
    ax_gamma.text(np.mean(x_gamma) - 1.5, 0.5, 'x2\nGamma')

    ax_exp.cla(); ax_exp.grid(True, alpha=0.25)
    ax_exp.hist(x_exp, bins=bins_exp, density=True, alpha=0.6)
    ax_exp.set_title("x3: Exponential + shift"); ax_exp.set_xlim(4, 14); ax_exp.set_ylim(0, 0.6)
    ax_exp.text(np.mean(x_exp) - 1.5, 0.5, 'x3\nExponential')

    ax_unif.cla(); ax_unif.grid(True, alpha=0.25)
    ax_unif.hist(x_unif, bins=bins_unif, density=True, alpha=0.6)
    ax_unif.set_title("x4: Uniform [14, 20]"); ax_unif.set_xlim(12, 22); ax_unif.set_ylim(0, 0.6)
    ax_unif.text(15.0, 0.5, 'x4\nUniform')

    return []

# Make the sliders live-update the current frame without restarting animation
def on_slider_change(val):
    # Force one immediate refresh using current frame index
    update(0)
    fig.canvas.draw_idle()

for sl in (s_mu, s_sig, s_k, s_theta, s_lambda, s_shift, s_n):
    sl.on_changed(on_slider_change)

# ~20 seconds total at 50 ms per frame and 400 frames
anim = FuncAnimation(fig, update, init_func=init, frames=400, interval=50, blit=False, repeat=True)

plt.show()
anim.save("distributions.gif", writer=PillowWriter(fps=20))