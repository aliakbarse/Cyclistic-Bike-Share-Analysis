"""Draw the six analysis charts from the clean Cyclistic table.

Each chart is one function that takes the prepared data and returns a
matplotlib figure; make_all() saves the six PNG files to docs/images/.
Chart titles state the finding, and the claims they make are checked
against the numbers in docs/findings.md.

Colours: member = blue, casual = orange. The two colours were checked for
colour-blind separation. The same colours are used in the Power BI report.

Run with: python -m cyclistic.plot_charts
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw to files, no window

import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mtick  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

from cyclistic import analysis, config  # noqa: E402

COLOR = {"member": "#2a78d6", "casual": "#eb6834"}
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
ORDER = analysis.RIDER_ORDER

STYLE = {
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE, "axes.edgecolor": GRID,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "text.color": INK, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.axisbelow": True, "font.size": 10, "axes.titlesize": 12,
    "axes.titleweight": "bold", "axes.titlelocation": "left",
    "legend.frameon": False,
}

PERCENT = mtick.PercentFormatter(decimals=0)


def hourly_profile_chart(df: pd.DataFrame):
    hourly = analysis.hourly_profile(df)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    for ax, day_type in zip(axes, ["Weekday", "Weekend"]):
        for rider in ORDER:
            s = hourly[
                (hourly["member_casual"] == rider) & (hourly["day_type"] == day_type)
            ]
            ax.plot(s["hour"], s["share_pct"], color=COLOR[rider], lw=2,
                    label=rider.capitalize(), solid_capstyle="round")
        ax.set_title(day_type)
        ax.set_xlabel("Start hour")
        ax.set_xticks(range(0, 24, 3))
        ax.yaxis.set_major_formatter(PERCENT)

    peak = hourly[(hourly["day_type"] == "Weekday") & (hourly["hour"] == 8)]
    peak = peak.set_index("member_casual")["share_pct"]
    for rider in ORDER:
        axes[0].plot(8, peak[rider], "o", color=COLOR[rider], ms=7,
                     mec=SURFACE, mew=2)
    top = hourly["share_pct"].max()
    for rider, ypos in zip(ORDER, (top * 0.95, top * 0.86)):
        axes[0].annotate(f"08:00  {rider} {peak[rider]:.1f}%", (8, peak[rider]),
                         xytext=(0.3, ypos), fontsize=9, color=INK2,
                         arrowprops=dict(arrowstyle="-", color=GRID))
    axes[0].set_ylabel("Share of rider type's rides")
    axes[0].legend(loc="upper right")
    fig.suptitle(
        f"Weekdays: {peak['member']:.1f}% of member rides start at 08:00, against "
        f"{peak['casual']:.1f}% for casual riders. Weekends: almost identical hours",
        x=0.01, ha="left", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return fig


def weekday_hour_heatmap_chart(df: pd.DataFrame):
    heat = analysis.weekday_hour_heatmap(df)
    vmax = heat["share_pct"].max()
    ramps = {
        "member": LinearSegmentedColormap.from_list("m", ["#eef5fd", "#2a78d6", "#0d366b"]),
        "casual": LinearSegmentedColormap.from_list("c", ["#fdf0ea", "#eb6834", "#7a2a0c"]),
    }
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.8), sharey=True)
    for ax, rider in zip(axes, ORDER):
        grid = (
            heat[heat["member_casual"] == rider]
            .pivot(index="day_of_week", columns="hour", values="share_pct")
            .reindex(analysis.WEEKDAY_NAMES)
            .reindex(columns=range(24))
            .fillna(0)
        )
        im = ax.imshow(grid.values, aspect="auto", cmap=ramps[rider], vmin=0, vmax=vmax)
        ax.set_title(rider.capitalize())
        ax.grid(False)
        ax.set_xticks(range(0, 24, 3))
        ax.set_xlabel("Start hour")
        ax.set_yticks(range(7))
        ax.set_yticklabels([d[:3] for d in analysis.WEEKDAY_NAMES])
        cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
        cb.set_label("% of rider type's rides", color=INK2)
        cb.outline.set_visible(False)
    fig.suptitle(
        "Weekday x hour: members concentrate on weekday commute hours; "
        "casual riders on weekend afternoons",
        x=0.01, ha="left", fontsize=13, fontweight="bold")
    fig.tight_layout()
    return fig


def monthly_chart(df: pd.DataFrame):
    monthly = analysis.monthly_rides(df)
    labels = pd.to_datetime(monthly.index, format="%Y%m").strftime("%b\n%y")
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11, 6.2), sharex=True, height_ratios=[2.2, 1])
    x = np.arange(len(monthly))
    w = 0.36
    for i, rider in enumerate(ORDER):
        ax1.bar(x + (i - 0.5) * (w + 0.04), monthly[rider] / 1000, width=w,
                color=COLOR[rider], label=rider.capitalize())
    ax1.set_ylabel("Rides (thousands)")
    ax1.legend(loc="upper left")
    ax1.set_title("Both groups ride more in summer, but casual riders swing far more")
    ax2.plot(x, monthly["casual_share_pct"], color=COLOR["casual"], lw=2,
             solid_capstyle="round")
    ax2.plot(x, monthly["casual_share_pct"], "o", color=COLOR["casual"], ms=7,
             mec=SURFACE, mew=2)
    for idx in (monthly["casual_share_pct"].idxmin(), monthly["casual_share_pct"].idxmax()):
        i = list(monthly.index).index(idx)
        v = monthly.loc[idx, "casual_share_pct"]
        ax2.annotate(f"{v:.0f}%", (i, v), xytext=(0, 9), textcoords="offset points",
                     ha="center", color=INK2)
    ax2.set_ylabel("Casual share of rides")
    ax2.set_ylim(0, 50)
    ax2.yaxis.set_major_formatter(PERCENT)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels)
    fig.tight_layout()
    return fig


def duration_chart(df: pd.DataFrame):
    bucket = analysis.duration_bucket_shares(df)
    fig, ax = plt.subplots(figsize=(8, 4))
    cats = analysis.DURATION_LABELS
    x = np.arange(len(cats))
    w = 0.36
    for i, rider in enumerate(ORDER):
        vals = (
            bucket[bucket["member_casual"] == rider]
            .set_index("duration_bucket")["share_pct"]
            .reindex(cats)
            .fillna(0)
        )
        bars = ax.bar(x + (i - 0.5) * (w + 0.04), vals, width=w,
                      color=COLOR[rider], label=rider.capitalize())
        for j in (0, len(cats) - 1):  # label only the two ends of the scale
            ax.text(bars[j].get_x() + w / 2, vals.iloc[j] + 1,
                    f"{vals.iloc[j]:.0f}%", ha="center", fontsize=9, color=INK2)
    ax.set_xticks(x)
    ax.set_xticklabels(cats)
    ax.set_ylabel("Share of rider type's rides")
    ax.yaxis.set_major_formatter(PERCENT)
    ax.legend()
    ax.set_title("Casual riders take longer rides more often")
    fig.tight_layout()
    return fig


def top_stations_chart(df: pd.DataFrame):
    top = analysis.top_casual_stations(df, 10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    bars = ax.barh(top["name"].astype(str), top["casual"] / 1000, height=0.6,
                   color=COLOR["casual"])
    for bar, (_, row) in zip(bars, top.iterrows()):
        ax.text(bar.get_width() + 0.6, bar.get_y() + bar.get_height() / 2,
                f"{row['casual_share_pct']:.0f}% casual", va="center",
                fontsize=9, color=INK2)
    ax.set_xlabel("Casual rides starting here (thousands)")
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, top["casual"].max() / 1000 * 1.25)
    ax.set_title("Casual riders' busiest start stations are lakefront and tourist sites")
    fig.tight_layout()
    return fig


def behaviour_chart(df: pd.DataFrame):
    profile = analysis.behaviour_profile(df)
    fig, ax = plt.subplots(figsize=(9, 4.2))
    x = np.arange(profile.shape[1])
    w = 0.36
    for i, rider in enumerate(ORDER):
        bars = ax.bar(x + (i - 0.5) * (w + 0.04), profile.loc[rider], width=w,
                      color=COLOR[rider], label=rider.capitalize())
        for bar, value in zip(bars, profile.loc[rider]):
            ax.text(bar.get_x() + w / 2, value + 1, f"{value:.0f}%",
                    ha="center", fontsize=9, color=INK2)
    ax.set_xticks(x)
    ax.set_xticklabels(profile.columns)
    ax.yaxis.set_major_formatter(PERCENT)
    ax.set_ylim(0, 85)
    ax.set_ylabel("Share of rider type's rides")
    ax.legend()
    ax.set_title("Casual riders skew to weekends and summer, with fewer commute-like rides")
    fig.tight_layout()
    return fig


CHARTS = {
    "01_hourly_profile.png": hourly_profile_chart,
    "02_weekday_hour_heatmap.png": weekday_hour_heatmap_chart,
    "03_monthly_rides_and_casual_share.png": monthly_chart,
    "04_duration_distribution.png": duration_chart,
    "05_top_casual_stations.png": top_stations_chart,
    "06_behaviour_profile.png": behaviour_chart,
}


def make_all(df: pd.DataFrame, out_dir: Path) -> list[Path]:
    """Draw every chart from a table that has the analysis fields."""
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    with plt.rc_context(STYLE):
        for name, draw in CHARTS.items():
            fig = draw(df)
            path = out_dir / name
            fig.savefig(path, dpi=160, bbox_inches="tight")
            plt.close(fig)
            saved.append(path)
            print(f"Saved {path}")
    return saved


def main() -> None:
    df = analysis.add_analysis_fields(analysis.load_clean())
    make_all(df, config.IMAGES_DIR)


if __name__ == "__main__":
    main()
