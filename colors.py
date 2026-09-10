"""
colors.py
---------
Converts raw fractal math (smoothed escape-time values + an "inside the
set" mask) into an RGBA image array matplotlib can display directly.

Kept separate from fractal.py so the numerical engine and the visual
styling are independent of each other -- you can swap in a different
palette without touching the math, and vice versa.
"""

import numpy as np
from matplotlib.colors import hsv_to_rgb

# Color of the "inside the set" region when NOT using a transparent
# background (pure black, matching a streetwear/poster aesthetic and
# blending cleanly onto black apparel).
INSIDE_COLOR = np.array([0.0, 0.0, 0.0])

# Controls how quickly the far-field background fades to black. Points
# that escape almost immediately (low smooth value -- empty space far
# from the fractal) previously got the same full-brightness hue treatment
# as the detailed boundary, producing a flat, blazing orange-red wash
# across the whole background. Ramping brightness (and, in transparent
# mode, alpha) up from 0 as smooth increases means only the actual
# fractal detail near the boundary is bright/opaque, and the background
# reads as solid black instead.
BACKGROUND_FADE = 14.0


def colorize(
    smooth: np.ndarray,
    inside: np.ndarray,
    hue_shift: float = 0.0,
    transparent_bg: bool = True,
) -> np.ndarray:
    """
    Map fractal data to an (H, W, 4) RGBA float array in [0, 1].

    Parameters
    ----------
    smooth         : smoothed escape-time array from compute_julia()
    inside         : boolean "never escaped" mask from compute_julia()
    hue_shift      : rotates the color wheel, in [0, 1) -- animating this
                     over time produces a color-cycling effect at near-zero
                     extra cost, since it doesn't require recomputing the
                     fractal itself
    transparent_bg : if True, the black far-field background also gets
                     alpha -> 0 (true transparency, ideal for compositing
                     onto apparel/print mockups). If False, the background
                     is still solid black, just opaque.

    Returns
    -------
    (H, W, 4) float array suitable for ax.imshow() or plt.imsave()
    """
    hue = (smooth * 0.012 + hue_shift) % 1.0
    saturation = np.full_like(hue, 0.85)
    # Brightness ramps from 0 (far-field background) to 1 (near the
    # fractal boundary / detail), instead of being uniformly 1 everywhere.
    value = np.clip(smooth / BACKGROUND_FADE, 0.0, 1.0)

    hsv = np.dstack([hue, saturation, value])
    rgb = hsv_to_rgb(hsv)
    rgb[inside] = INSIDE_COLOR

    if transparent_bg:
        alpha = value.copy()
        alpha[inside] = 0.0
    else:
        alpha = np.ones(smooth.shape, dtype=np.float64)

    return np.dstack([rgb, alpha])