# Interactive Julia Set Explorer

An interactive fractal generator implementing the **Julia set** using the
escape-time algorithm, vectorized with NumPy and rendered live with
Matplotlib. Built for **Design Lab 01 — Designing Using Fractals**.

## Fractal Type Implemented

- **Julia Set** (escape-time / iterative fractal, `z = z^2 + c`)
- Smooth (continuous, banding-free) coloring via the normalized iteration
  count method
- 2x supersampled anti-aliasing on exported images

## Tools, Languages & Libraries

- Python 3.10+
- [NumPy](https://numpy.org/) — vectorized escape-time computation
- [Matplotlib](https://matplotlib.org/) — interactive rendering, event
  handling, and animation
- [Pillow](https://python-pillow.org/) — animated GIF export

## Features / Creative Elements

- **Pan & zoom** with the mouse (drag to pan, scroll to zoom toward the cursor)
- **Live color-cycling animation** (toggle with `a`) — recolors the cached
  fractal each frame instead of recomputing it, so it stays smooth
- **Randomized Julia constants** (`c`) from a curated set of visually
  distinct fractal shapes
- **Transparent background export** — points inside the Julia set are
  rendered with alpha = 0
- **High-resolution PNG export** and **animated GIF export**, both
  supersampled for a clean, alias-free result

## Setup & Run Instructions

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd <repo-folder>

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the interactive explorer
python app.py
```

## Controls

| Input | Action |
|---|---|
| Left-click drag | Pan the view |
| Scroll wheel | Zoom in / out (centered on cursor) |
| `c` | Randomize the Julia constant `C` |
| `r` | Reset the view |
| `a` | Toggle color-cycling animation |
| `t` | Toggle transparent background |
| `↑` / `↓` | Increase / decrease max iterations |
| `s` | Save current view as a high-res PNG (see **Output Location** below) |
| `g` | Save a short animated GIF of the current view (see **Output Location** below) |

## Output Location

> **Note:** `OUTPUT_DIR` in `app.py` is currently set to an absolute,
> machine-specific path:
> `D:\Shaheer\Nust Parhai\Third Semester\Artificial Intelligence (AI)\Lab\Lab Solutions\fractal-lab\Output`
>
> `s` and `g` will only save correctly on this exact machine, with this
> exact folder present. If you clone this repo onto a different computer
> (including a grader's), either create that same folder structure first,
> or edit `OUTPUT_DIR` at the top of `app.py` back to a relative path
> (e.g. `"output"`) so it works anywhere.

## Project Structure

```
.
├── fractal.py     # Core escape-time math (NumPy, vectorized)
├── colors.py      # Maps fractal data -> RGBA image arrays
├── app.py         # Interactive Matplotlib application (entry point)
├── requirements.txt
└── output/        # Default export folder (see Output Location note above)
```

## Output

![Julia set screenshot](output/screenshot.png)

## Student

- **Name:** Shaheer Hasan Khan
- **Registration Number:** 543016
- **Course:** BS Computer Science — Design Lab 01

## Academic Integrity

This implementation was written from scratch for this lab. Open-source
libraries used (NumPy, Matplotlib, Pillow) are credited above.