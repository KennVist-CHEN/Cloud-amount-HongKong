# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib"]
# ///

"""
Read the file in data/, make one picture, save it to out/.

    uv run plot.py

Three parts, and you will replace all three: rows() reads the file the way *your*
file needs reading, the loop in main() picks the numbers out of it, and the plot at
the bottom is the transformation you chose. Print before you plot.
"""

import csv
from pathlib import Path

import matplotlib.pyplot as plt

FILE = "hko-daily-mean-cloud-2026.csv"
PICTURE = "plot.png"

HERE = Path(__file__).parent
DATA = HERE / "data" / FILE
OUT = HERE / "out"


def rows(path):
    """Keep only the lines that start with a year."""
    kept = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for line in csv.reader(handle):
            if line and line[0].isdigit():
                kept.append(line)
    return kept


def main():
    table = rows(DATA)
    print(f"{DATA.name}: {len(table)} rows. The first one: {table[0]}")

    days, values = [], []
    for i, (year, month, day, value, quality) in enumerate(table):
        if value == "***":
            continue
        days.append(i + 1)
        values.append(float(value))

    print(f"{len(values)} values, from {min(values)} to {max(values)}")

    # --- Cloud Cover visualisation ---
    fig, ax = plt.subplots(figsize=(12, 5))

    # Create one continuous cloud mass.
    ax.fill_between(
        days,
        values,
        0,
        alpha=0.35,
    )

    # Add a thin outline to show the changing cloud level.
    ax.plot(
        days,
        values,
        linewidth=1.0,
    )

    # Cloud amount is a percentage from 0 to 100.
    ax.set_ylim(0, 100)
    ax.set_xlim(1, len(days))

    # Reference levels.
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel("Daily mean cloud amount (%)")

    # Month positions for the x-axis.
    month_days = [1, 32, 60, 91, 121, 152, 182, 213]
    month_labels = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
    ]

    ax.set_xticks(month_days)
    ax.set_xticklabels(month_labels)

    ax.set_xlabel("2026")

    # Very subtle horizontal reference lines.
    ax.grid(
        axis="y",
        linewidth=0.5,
        alpha=0.15,
    )

    ax.set_axisbelow(True)

    # Remove unnecessary borders.
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Title.
    ax.set_title(
        "Cloud Cover — Hong Kong, 2026",
        loc="left",
        fontsize=18,
        pad=18,
    )

    # Small explanation.
    ax.text(
        0,
        -0.22,
        "Each day forms part of the cloud layer. "
        "Height = daily mean cloud amount.",
        transform=ax.transAxes,
        fontsize=9,
        alpha=0.6,
    )

    # Data source.
    ax.text(
        1,
        -0.22,
        "Source: Hong Kong Observatory",
        transform=ax.transAxes,
        fontsize=9,
        alpha=0.6,
        ha="right",
    )

    fig.tight_layout()

    OUT.mkdir(exist_ok=True)
    fig.savefig(
        OUT / PICTURE,
        dpi=200,
        bbox_inches="tight",
    )
    print(f"saved out/{PICTURE}")

    plt.show()


if __name__ == "__main__":
    main()
