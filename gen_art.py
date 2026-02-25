import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

fig, ax = plt.subplots(figsize=(4, 4), facecolor='black')
ax.set_facecolor('black')
ax.set_xlim(0, 400)
ax.set_ylim(0, 400)
ax.axis('off')
fig.tight_layout(pad=0)

N = 20000
scat = ax.scatter([], [], s=0.3, c='white', alpha=0.4, linewidths=0)

def compute(t):
    i = np.arange(N, dtype=float)
    y = i / 500.0
    k = np.cos(y * 5) * np.where(y < 11, 21, 11)
    e = y / 8 - 13
    o = np.sqrt(k**2 + e**2) / 6
    q = k * 2 + 49 + np.cos(y) / (k + 1e-9) + k * np.cos(y / 2) * (1 + np.sin(o * 4 - e / 2 - t))
    c = o / 1.5 - e / 5 - t / 8 + (i % 3) * 8
    x = q * np.sin(c) + 200
    yy = 230 + q * np.cos(c) - 79 * np.sin(c / 2)
    return x, yy

def init():
    scat.set_offsets(np.empty((0, 2)))
    return scat,

def update(frame):
    t = frame * np.pi / 45
    x, y = compute(t)
    mask = (x > 0) & (x < 400) & (y > 0) & (y < 400)
    pts = np.column_stack([x[mask], y[mask]])
    scat.set_offsets(pts)
    return scat,

frames = 90
ani = animation.FuncAnimation(fig, update, frames=frames, init_func=init, interval=1000/30, blit=True)

out = '/Users/shora-mini/shora-bot/suika-bot/kakusei.mp4'
writer = animation.FFMpegWriter(fps=30, bitrate=1800)
ani.save(out, writer=writer, dpi=100, savefig_kwargs={'facecolor': 'black'})
print(f'saved: {out}')
plt.close()
