"""Render the walking-vs-jumping confusion matrix as a PNG that matches
the v2 design tokens. One-shot; kept in the repo for reproducibility.

Usage:
    python scripts/render-wj-cm.py
Writes:
    assets/projects/walking-jumping-cm.png
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import numpy as np

# Numbers from the existing ASCII sample in index.html.
CM = np.array(
    [
        [182, 7],
        [5, 156],
    ]
)
LABELS = ["walk", "jump"]
ACCURACY = 0.965
F1 = 0.964

# v2 design tokens (dark theme).
BG = "#0a0e14"
FG = "#d6dee6"
DIM = "#8a96a3"
GRID = "#1c2330"
ACCENT = "#f5b342"

OUT = Path(__file__).resolve().parent.parent / "assets" / "projects" / "walking-jumping-cm.png"


def main() -> None:
    # Build a custom diverging colormap that goes from --bg-grid (off-diag)
    # to --accent (max diag). Diagonal cells will land near the high end.
    from matplotlib.colors import LinearSegmentedColormap

    cmap = LinearSegmentedColormap.from_list("v2_amber", [GRID, ACCENT])

    # We want strong colors on the diagonal and quiet ones off-diagonal,
    # so normalize by the overall max rather than per-row.
    norm_values = CM.astype(float) / CM.max()

    fig, ax = plt.subplots(figsize=(6, 4), dpi=110, facecolor=BG)
    ax.set_facecolor(BG)

    ax.imshow(norm_values, cmap=cmap, vmin=0, vmax=1, aspect="auto")

    # Cell text — dark on the bright diagonal, light on the muted cells.
    for r in range(CM.shape[0]):
        for c in range(CM.shape[1]):
            value = int(CM[r, c])
            color = BG if norm_values[r, c] > 0.5 else FG
            ax.text(
                c, r, str(value),
                ha="center", va="center",
                color=color,
                fontsize=18,
                fontfamily="monospace",
                fontweight="bold",
            )

    # Axes labels and ticks.
    ax.set_xticks(range(len(LABELS)))
    ax.set_yticks(range(len(LABELS)))
    ax.set_xticklabels([f"pred {l}" for l in LABELS], color=FG, fontfamily="monospace")
    ax.set_yticklabels([f"true {l}" for l in LABELS], color=FG, fontfamily="monospace")
    ax.tick_params(colors=FG, length=0)

    for spine in ax.spines.values():
        spine.set_color(GRID)

    ax.set_title(
        "confusion matrix — walking vs jumping",
        color=FG, fontfamily="monospace", fontsize=12, pad=14, loc="left",
    )
    fig.text(
        0.02, 0.02,
        f"// accuracy {ACCURACY:.3f}  ·  f1 {F1:.3f}",
        color=DIM, fontfamily="monospace", fontsize=10,
    )

    fig.tight_layout(rect=(0, 0.06, 1, 1))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, facecolor=BG, dpi=110)
    plt.close(fig)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
