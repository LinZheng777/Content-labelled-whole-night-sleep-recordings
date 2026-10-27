"""
Plot pie charts for Fig. 2d.

Input
-----
Fig2d.csv
    Required columns:
    - variables
    - descr_1, descr_2, descr_3, descr_4, descr_5
    - score_1, score_2, score_3, score_4, score_5

Usage
-----
python Fig2d.py

The CSV file should be placed in the same folder as this script.
"""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import Patch
from matplotlib.legend_handler import HandlerPatch


# ---------------------------------------------------------------------
# Figure settings
# ---------------------------------------------------------------------
rcParams["font.family"] = "serif"
rcParams["font.serif"] = ["Times New Roman"]
rcParams["svg.fonttype"] = "none"


class HandlerCircle(HandlerPatch):
    """Display legend patch handles as circles."""

    def create_artists(
        self,
        legend,
        orig_handle,
        xdescent,
        ydescent,
        width,
        height,
        fontsize,
        trans,
    ):
        center = (0.5 * width, 0.5 * height)
        radius = 0.5 * min(width, height)

        patch = plt.Circle(
            center,
            radius,
            facecolor=orig_handle.get_facecolor(),
            edgecolor=orig_handle.get_edgecolor(),
        )

        self.update_prop(patch, orig_handle, legend)
        patch.set_transform(trans)

        return [patch]


# ---------------------------------------------------------------------
# Input path
# ---------------------------------------------------------------------
# The CSV file should be placed in the same folder as this script.
# To use an absolute path, replace the following line, for example:
# data_file = Path(r"I:\second_resource\code_submit\Fig.2\Fig2d.csv")
script_dir = Path(__file__).resolve().parent
data_file = script_dir / "Fig2d.csv"


# ---------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------
data = pd.read_csv(data_file)

required_cols = (
    ["variables"]
    + [f"descr_{i}" for i in range(1, 6)]
    + [f"score_{i}" for i in range(1, 6)]
)

missing_cols = [col for col in required_cols if col not in data.columns]

if missing_cols:
    raise ValueError(f"Missing required columns in {data_file}: {missing_cols}")


# ---------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------
colors = ["#8AC6D1", "#BBDED6", "#FAE3D9", "#FFB6B9", "#D3F6F3"]

for row_idx, row in data.iterrows():
    variable_name = row["variables"]

    labels = [row[f"descr_{i}"] for i in range(1, 6)]
    sizes = [row[f"score_{i}"] for i in range(1, 6)]

    fig, ax = plt.subplots(figsize=(6, 4))

    wedges, texts, autotexts = ax.pie(
        sizes,
        colors=colors,
        autopct="%1.1f%%",
        startangle=140,
    )

    handles = [
        Patch(facecolor=color, edgecolor=color)
        for color in colors
    ]

    ax.legend(
        handles,
        labels,
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        handler_map={Patch: HandlerCircle()},
        frameon=False,
    )

    ax.axis("equal")
    ax.set_title(str(variable_name), fontsize=13, fontweight="bold")

    plt.setp(autotexts, size=10, weight="bold", color="black")
    plt.setp(texts, size=12, weight="bold")

    fig.subplots_adjust(left=0.125, right=0.70, top=0.88, bottom=0.11)

    plt.show()