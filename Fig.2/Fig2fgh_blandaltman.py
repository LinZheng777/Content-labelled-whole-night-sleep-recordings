"""
Fig2fgh_blandaltman.py

Purpose
-------
Bland-Altman analysis of self-reported, EEG-derived and actigraphy-derived
TST and WASO (cued night), quantifying the subjective-objective discrepancy
raised by Reviewer 2, Comment 3.

Six panels mirroring the layout of the original Fig2fgh correlation figure:
    row 1: TST   - Self-report vs EEG | Self-report vs Actigraphy | EEG vs Actigraphy
    row 2: WASO  - same three modality pairs

Each panel shows
    - x: mean of the two measures ((m1 + m2) / 2)
    - y: difference (m1 - m2), i.e. positive = m1 overestimates
    - solid line: mean bias; dashed lines: 95% limits of agreement (bias +/- 1.96 SD)

Input
-----
Fig2fgh.csv (same folder; columns: subjects, WASO_scale, TST_scale,
WASO, TST, WASO_watch, TST_watch). Subjects 1-135 by default, matching the
original Fig2fgh analysis sample.

Output
------
Fig2fgh_blandaltman.svg        vector figure
Fig2fgh_blandaltman.png        preview
Fig2fgh_blandaltman_stats.csv  bias / LoA / N / proportional-bias per panel
                               (for the response letter)

Usage
-----
python Fig2fgh_blandaltman.py [--subjects-min 1] [--subjects-max 135]
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats as sps

plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["font.family"] = "Arial"
sns.set_theme(style="white", palette="muted")

SCRIPT_DIR = Path(__file__).resolve().parent

PANELS = [
    # (m1, m2, title, m1_label, m2_label) — difference = m1 - m2
    ("TST_scale", "TST",        "TST: Self-report vs EEG",         "Self-report", "EEG"),
    ("TST_scale", "TST_watch",  "TST: Self-report vs Actigraphy",  "Self-report", "Actigraphy"),
    ("TST",       "TST_watch",  "TST: EEG vs Actigraphy",          "EEG",         "Actigraphy"),
    ("WASO_scale", "WASO",       "WASO: Self-report vs EEG",        "Self-report", "EEG"),
    ("WASO_scale", "WASO_watch", "WASO: Self-report vs Actigraphy", "Self-report", "Actigraphy"),
    ("WASO",       "WASO_watch", "WASO: EEG vs Actigraphy",         "EEG",         "Actigraphy"),
]


def bland_altman(d, m1, m2):
    """Return BA statistics for the pairwise-complete rows of d."""
    sub = d[[m1, m2]].dropna()
    mean_xy = (sub[m1] + sub[m2]) / 2.0
    diff = sub[m1] - sub[m2]
    bias = diff.mean()
    sd = diff.std(ddof=1)
    loa_lo, loa_hi = bias - 1.96 * sd, bias + 1.96 * sd
    # proportional bias: OLS of difference on mean
    slope, intercept, r, p_slope, _ = sps.linregress(mean_xy, diff)
    return {
        "n": len(sub), "mean_pair": mean_xy, "diff": diff,
        "bias": bias, "sd": sd, "loa_lo": loa_lo, "loa_hi": loa_hi,
        "slope": slope, "p_slope": p_slope,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default=str(SCRIPT_DIR / "Fig2fgh.csv"))
    ap.add_argument("--subjects-min", type=int, default=1)
    ap.add_argument("--subjects-max", type=int, default=135,
                    help="135 = main analysis sample of the original Fig2fgh figure")
    ap.add_argument("--out-prefix", default=str(SCRIPT_DIR / "Fig2fgh_blandaltman"))
    args = ap.parse_args()

    df = pd.read_csv(args.data)
    for c in df.columns[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df[df["subjects"].between(args.subjects_min, args.subjects_max)].copy()
    print("subjects %d-%d: %d rows" % (args.subjects_min, args.subjects_max, len(df)))

    # marginal means (context for the Table 1 / reviewer arithmetic)
    for c in ["TST_scale", "TST", "TST_watch", "WASO_scale", "WASO", "WASO_watch"]:
        print("  mean %-10s = %7.1f min (n=%d)" % (c, df[c].mean(), df[c].notna().sum()))

    # ------------------------------------------------------------------ plot
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.subplots_adjust(hspace=0.4, wspace=0.3)

    rows_stats = []
    for k, (m1, m2, title, l1, l2) in enumerate(PANELS):
        ax = axes[k // 3, k % 3]
        ba = bland_altman(df, m1, m2)
        rows_stats.append({
            "panel": title, "measure": m1.replace("_scale", " (self)") if "_scale" in m1 else m1,
            "m1": m1, "m2": m2, "n": ba["n"],
            "bias_min": ba["bias"], "sd_min": ba["sd"],
            "loa_lower": ba["loa_lo"], "loa_upper": ba["loa_hi"],
            "prop_bias_slope": ba["slope"], "prop_bias_p": ba["p_slope"],
        })

        ax.scatter(ba["mean_pair"], ba["diff"], s=28, alpha=0.45,
                   color="#4C72B0", edgecolor="none")
        ax.axhline(ba["bias"], color="#C44E52", lw=2.5)
        ax.axhline(ba["loa_lo"], color="#C44E52", lw=1.4, ls="--")
        ax.axhline(ba["loa_hi"], color="#C44E52", lw=1.4, ls="--")

        stat_text = (
            "bias = %+.1f min\n"
            "LoA = [%.1f, %.1f]\n"
            "N = %d" % (ba["bias"], ba["loa_lo"], ba["loa_hi"], ba["n"])
        )
        ax.text(0.05, 0.95, stat_text, transform=ax.transAxes,
                verticalalignment="top", fontsize=11, fontweight="bold",
                bbox={"boxstyle": "round", "facecolor": "white",
                      "alpha": 0.7, "edgecolor": "none"})

        ax.set_title(title, fontsize=14, pad=15)
        ax.set_xlabel("Mean of %s and %s (min)" % (l1, l2))
        ax.set_ylabel("%s $-$ %s (min)" % (l1, l2))
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    out_csv = args.out_prefix + "_stats.csv"
    pd.DataFrame(rows_stats).to_csv(out_csv, index=False, encoding="utf-8-sig")

    fig.tight_layout()
    fig.savefig(args.out_prefix + ".svg", dpi=300, bbox_inches="tight")
    fig.savefig(args.out_prefix + ".png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    print("\n=== Bland-Altman summary ===")
    for r in rows_stats:
        print("%-34s n=%3d  bias=%+7.1f  LoA=[%+7.1f, %+7.1f]  slope p=%.3g" % (
            r["panel"], r["n"], r["bias_min"], r["loa_lower"], r["loa_upper"],
            r["prop_bias_p"]))
    print("\nsaved: %s.svg / .png / _stats.csv" % args.out_prefix)


if __name__ == "__main__":
    main()
