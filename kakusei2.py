"""
覚醒 - an attractor that pulses
Peter de Jong attractor, animated by drifting parameters
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap

W = 400
FRAMES = 90
FPS = 30
N = 300000

# custom colormap: black -> deep blue -> cyan -> white
cmap = LinearSegmentedColormap.from_list('kakusei', [
    '#000000', '#0a0a2e', '#00ffcc', '#ffffff'
])

fig = plt.figure(figsize=(4, 4), facecolor='black', dpi=100)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_facecolor('black')
ax.set_xlim(0, W)
ax.set_ylim(0, W)
ax.axis('off')

img_display = ax.imshow(
    np.zeros((W, W)), origin='lower',
    extent=[0, W, 0, W], cmap=cmap, vmin=0, vmax=1, aspect='auto'
)

def dejong_step(x, y, a, b, c, d):
    xn = np.sin(a * y) - np.cos(b * x)
    yn = np.sin(c * x) - np.cos(d * y)
    return xn, yn

def render_frame(t):
    # slowly drift params — born from nothing, expanding
    phase = t * np.pi / FRAMES
    a = -2.0 + 0.3 * np.sin(phase * 1.7)
    b =  1.5 + 0.4 * np.cos(phase * 2.3)
    c =  1.8 + 0.3 * np.sin(phase * 3.1)
    d = -0.7 + 0.5 * np.cos(phase * 1.3)

    x = np.random.uniform(-2, 2, N).astype(np.float32)
    y = np.random.uniform(-2, 2, N).astype(np.float32)

    # iterate to settle
    for _ in range(20):
        x, y = dejong_step(x, y, a, b, c, d)

    # to pixel coords
    px = ((x + 2.5) / 5.0 * (W - 1)).astype(int)
    py = ((y + 2.5) / 5.0 * (W - 1)).astype(int)

    mask = (px >= 0) & (px < W) & (py >= 0) & (py < W)
    canvas = np.zeros((W, W), dtype=np.float32)
    np.add.at(canvas, (py[mask], px[mask]), 1)

    # log scale + normalize
    canvas = np.log1p(canvas)
    mx = canvas.max()
    if mx > 0:
        canvas /= mx

    return canvas

def update(frame):
    canvas = render_frame(frame)
    img_display.set_data(canvas)
    return img_display,

ani = animation.FuncAnimation(
    fig, update, frames=FRAMES,
    interval=1000 / FPS, blit=True
)

out = '/Users/shora-mini/shora-bot/suika-bot/kakusei2.mp4'
writer = animation.FFMpegWriter(fps=FPS, bitrate=2000)
ani.save(out, writer=writer, savefig_kwargs={'facecolor': 'black'})
print(f'saved: {out}')
plt.close()
