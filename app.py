"""
app.py
------
Interactive Julia set explorer built on matplotlib.

Run with:
    python app.py

Controls
    Drag (left mouse)  : pan
    Scroll wheel       : zoom in / out (centered on the cursor)
    'c'                : jump to a random curated Julia constant
    'r'                : reset the view
    'a'                : toggle color-cycling animation
    't'                : toggle transparent background (inside-of-set alpha)
    Up / Down arrow     : increase / decrease max iterations (more detail)
    's'                : save the current view as a high-resolution PNG
    'g'                : save a short animated GIF of the current view
"""

import os
import random
import time

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

from fractal import compute_julia, compute_julia_supersampled, CURATED_CONSTANTS
from colors import colorize

LIVE_RESOLUTION = 700
EXPORT_RESOLUTION = 2400
DEFAULT_C = complex(-0.7, 0.27015)
# NOTE: this is an absolute, machine-specific path. 's' and 'g' will save
# here on this computer only -- cloning this repo onto any other machine
# (including a grader's) and running app.py will raise FileNotFoundError
# unless this folder exists at this exact location, or is created first.
OUTPUT_DIR = r"D:\Shaheer\Nust Parhai\Third Semester\Artificial Intelligence (AI)\Lab\Lab Solutions\fractal-lab\Output"

INSTRUCTIONS = """
Julia Set Explorer -- Controls
  Drag (left mouse)   : pan
  Scroll wheel        : zoom in / out
  'c'                 : randomize the Julia constant C
  'r'                 : reset view
  'a'                 : toggle color-cycling animation
  't'                 : toggle transparent background
  Up / Down arrow      : increase / decrease max iterations
  's'                 : save current view as a high-res PNG (output/)
  'g'                 : save a short animated GIF of the current view (output/)
"""


class JuliaExplorer:
    """Owns all fractal state and wires matplotlib events to it."""

    def __init__(self):
        self.width = LIVE_RESOLUTION
        self.height = LIVE_RESOLUTION
        self.center = [0.0, 0.0]
        self.scale = 1.5
        self.c = DEFAULT_C
        self.max_iter = 200
        self.hue_shift = 0.0
        self.animate = False
        self.transparent = True

        self._drag_start = None
        self._drag_center_start = None
        self.smooth = None
        self.inside = None
        self.im = None

        self.fig, self.ax = plt.subplots(figsize=(7, 7), facecolor="#0a0a0f")
        self.ax.set_facecolor("#0a0a0f")
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self._title = None

        self._connect_events()
        self._recompute()
        self._redraw_colors()

        # Color animation runs on a timer but only actually recolors
        # when self.animate is True -- recoloring is cheap (no fractal
        # recomputation), so this stays smooth.
        self.anim = animation.FuncAnimation(
            self.fig, self._animate_step, interval=60, cache_frame_data=False
        )

    # ---- wiring -----------------------------------------------------

    def _connect_events(self):
        self.fig.canvas.mpl_connect("scroll_event", self.on_scroll)
        self.fig.canvas.mpl_connect("button_press_event", self.on_press)
        self.fig.canvas.mpl_connect("button_release_event", self.on_release)
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_motion)
        self.fig.canvas.mpl_connect("key_press_event", self.on_key)

    # ---- core render steps -------------------------------------------

    def _recompute(self):
        self.smooth, self.inside = compute_julia(
            self.width, self.height, tuple(self.center), self.scale, self.c, self.max_iter
        )

    def _redraw_colors(self):
        rgba = colorize(self.smooth, self.inside, self.hue_shift, self.transparent)
        if self.im is None:
            self.im = self.ax.imshow(rgba, origin="lower")
            self._title = self.ax.set_title(
                self._title_text(), color="#00fff0", fontsize=9, family="monospace"
            )
        else:
            self.im.set_data(rgba)
            self._title.set_text(self._title_text())
        self.fig.canvas.draw_idle()

    def _title_text(self):
        sign = "+" if self.c.imag >= 0 else ""
        zoom = 1.5 / self.scale
        return f"C = {self.c.real:.3f}{sign}{self.c.imag:.3f}i   zoom {zoom:.2f}x   iter {self.max_iter}"

    def _animate_step(self, _frame):
        if self.animate:
            self.hue_shift = (self.hue_shift + 0.004) % 1.0
            self._redraw_colors()

    # ---- mouse events -------------------------------------------------

    def on_scroll(self, event):
        if event.xdata is None or event.ydata is None:
            return
        factor = 0.88 if event.button == "up" else 1.14
        self.center[0] = event.xdata + (self.center[0] - event.xdata) * factor
        self.center[1] = event.ydata + (self.center[1] - event.ydata) * factor
        self.scale = float(np.clip(self.scale * factor, 0.0005, 3.0))
        self._recompute()
        self._redraw_colors()

    def on_press(self, event):
        if event.button == 1 and event.xdata is not None:
            self._drag_start = (event.xdata, event.ydata)
            self._drag_center_start = tuple(self.center)

    def on_motion(self, event):
        if self._drag_start is None or event.xdata is None:
            return
        dx = event.xdata - self._drag_start[0]
        dy = event.ydata - self._drag_start[1]
        self.center[0] = self._drag_center_start[0] - dx
        self.center[1] = self._drag_center_start[1] - dy
        self._recompute()
        self._redraw_colors()

    def on_release(self, _event):
        self._drag_start = None

    # ---- keyboard events -----------------------------------------------

    def on_key(self, event):
        if event.key == "r":
            self.center = [0.0, 0.0]
            self.scale = 1.5
            self._recompute()
            self._redraw_colors()
        elif event.key == "c":
            self.c = random.choice(CURATED_CONSTANTS)
            self._recompute()
            self._redraw_colors()
        elif event.key == "a":
            self.animate = not self.animate
        elif event.key == "t":
            self.transparent = not self.transparent
            self._redraw_colors()
        elif event.key == "up":
            self.max_iter = min(600, self.max_iter + 25)
            self._recompute()
            self._redraw_colors()
        elif event.key == "down":
            self.max_iter = max(25, self.max_iter - 25)
            self._recompute()
            self._redraw_colors()
        elif event.key == "s":
            self.save_high_res()
        elif event.key == "g":
            self.save_gif()

    # ---- export ---------------------------------------------------------

    def save_high_res(self, resolution: int = EXPORT_RESOLUTION):
        print(f"Rendering high-res export at {resolution}x{resolution} (2x supersampled) ...")
        smooth, inside = compute_julia_supersampled(
            resolution, resolution, tuple(self.center), self.scale, self.c, self.max_iter,
            supersample=2,
        )
        rgba = colorize(smooth, inside, self.hue_shift, self.transparent)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        path = os.path.join(OUTPUT_DIR, f"julia_{int(time.time())}.png")
        plt.imsave(path, rgba, origin="lower")
        print(f"Saved {path}")

    def save_gif(self, frames: int = 40, resolution: int = 400):
        print("Rendering animated GIF preview ...")
        from PIL import Image

        smooth, inside = compute_julia(
            resolution, resolution, tuple(self.center), self.scale, self.c, self.max_iter
        )
        images = []
        for i in range(frames):
            hue = (i / frames) % 1.0
            rgba = colorize(smooth, inside, hue, self.transparent)
            rgb = (rgba[..., :3] * 255).astype("uint8")
            images.append(Image.fromarray(np.flipud(rgb)))

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        path = os.path.join(OUTPUT_DIR, f"julia_{int(time.time())}.gif")
        images[0].save(path, save_all=True, append_images=images[1:], duration=60, loop=0)
        print(f"Saved {path}")

    # ---- entry point ------------------------------------------------------

    def run(self):
        print(INSTRUCTIONS)
        plt.show()


def main():
    explorer = JuliaExplorer()
    explorer.run()


if __name__ == "__main__":
    main()