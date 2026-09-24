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

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(days, values, linewidth=1.5)
    ax.set_xlabel("day of 2026")
    ax.set_ylabel("daily mean cloud amount, %")
    ax.set_title("Hong Kong Observatory, Daily Mean Cloud Amount in 2026")
    fig.tight_layout()

    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / PICTURE, dpi=150)
    print(f"saved out/{PICTURE}")

    plt.show()


if __name__ == "__main__":
    main()
