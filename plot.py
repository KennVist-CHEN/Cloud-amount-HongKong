# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib"]
# ///

"""
Read the file in data/, make one picture, save it to out/.

    uv run plot.py

The raw daily cloud-cover values are preserved.
A 7-day moving average is used only to create a softer visual cloud boundary.
"""

import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.path import Path as PlotPath
from matplotlib.patches import PathPatch
from matplotlib.colors import LinearSegmentedColormap


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


def moving_average(values, window=7):
    """Smooth the visual cloud boundary without changing raw data."""
    smoothed = []

    half = window // 2

    for i in range(len(values)):
        start = max(0, i - half)
        end = min(len(values), i + half + 1)

        section = values[start:end]
        smoothed.append(sum(section) / len(section))

    return smoothed


def smooth_path(x, y):
    """Create a smooth curve through the visual data points."""
    vertices = [(x[0], y[0])]
    codes = [PlotPath.MOVETO]

    for i in range(len(x) - 1):
        x0, y0 = x[max(0, i - 1)], y[max(0, i - 1)]
        x1, y1 = x[i], y[i]
        x2, y2 = x[i + 1], y[i + 1]
        x3, y3 = x[min(len(x) - 1, i + 2)], y[min(len(y) - 1, i + 2)]

        # Cubic Bézier control points.
        c1 = (
            x1 + (x2 - x0) / 6,
            y1 + (y2 - y0) / 6,
        )

        c2 = (
            x2 - (x3 - x1) / 6,
            y2 - (y3 - y1) / 6,
        )

        vertices.extend([
            c1,
            c2,
            (x2, y2),
        ])

        codes.extend([
            PlotPath.CURVE4,
            PlotPath.CURVE4,
            PlotPath.CURVE4,
        ])

    return PlotPath(vertices, codes)


def make_cloud_shape(days, values):
    """Create a closed cloud shape from the smoothed boundary."""

    cloud_path = smooth_path(days, values)

    cloud_vertices = list(cloud_path.vertices)

    # Close the cloud down to 0%.
    cloud_vertices.extend([
        (days[-1], 0),
        (days[0], 0),
        (days[0], values[0]),
    ])

    cloud_codes = list(cloud_path.codes)

    cloud_codes.extend([
        PlotPath.LINETO,
        PlotPath.LINETO,
        PlotPath.CLOSEPOLY,
    ])

    return PlotPath(
        cloud_vertices,
        cloud_codes,
    )


def draw_sky_gradient(fig):
    """Draw a vertical sky gradient across the entire figure."""

    sky_top = "#D8EEF8"
    sky_bottom = "#F1FAFD"

    sky_cmap = LinearSegmentedColormap.from_list(
        "sky",
        [
            sky_top,
            sky_bottom,
        ],
    )

    # Create a full-figure background axes.
    background = fig.add_axes(
        [0, 0, 1, 1],
        zorder=0,
    )

    background.imshow(
        [[0], [1]],
        cmap=sky_cmap,
        aspect="auto",
        extent=(0, 1, 0, 1),
        origin="upper",
        interpolation="bicubic",
    )

    background.axis("off")

    return sky_bottom


def main():
    table = rows(DATA)

    print(
        f"{DATA.name}: {len(table)} rows. "
        f"The first one: {table[0]}"
    )

    days, values = [], []

    # Pick the numerical values out of the CSV.
    for i, (year, month, day, value, quality) in enumerate(table):
        if value == "***":
            continue

        days.append(i + 1)
        values.append(float(value))

    print(
        f"{len(values)} values, "
        f"from {min(values)} to {max(values)}"
    )

    # ---------------------------------------------------------
    # Figure
    # ---------------------------------------------------------

    fig = plt.figure(figsize=(12, 5))

    # Draw the sky over the entire figure.
    sky_bottom = draw_sky_gradient(fig)

    # Main chart area.
    ax = fig.add_axes(
        [0.075, 0.22, 0.91, 0.64],
        zorder=2,
    )

    ax.patch.set_alpha(0)

    # ---------------------------------------------------------
    # Colors
    # ---------------------------------------------------------

    cloud_white = "#FFFFFF"
    text_blue = "#54707D"
    axis_blue = "#9FC2D1"

    # ---------------------------------------------------------
    # Smooth visual cloud boundary
    #
    # Raw values remain unchanged.
    # Only the visual boundary uses the 7-day average.
    # ---------------------------------------------------------

    smooth_values = moving_average(
        values,
        window=7,
    )

    cloud_shape = make_cloud_shape(
        days,
        smooth_values,
    )

    # ---------------------------------------------------------
    # Main cloud body
    # ---------------------------------------------------------

    cloud = PathPatch(
        cloud_shape,
        facecolor=cloud_white,
        edgecolor="none",
        alpha=0.72,
        zorder=3,
    )

    ax.add_patch(cloud)

    # ---------------------------------------------------------
    # Soft cloud haze
    #
    # Several almost-transparent layers create a soft
    # atmospheric edge without drawing an outline.
    # ---------------------------------------------------------

    haze_layers = [
        (0.8, 0.10),
        (1.8, 0.055),
        (3.2, 0.025),
        (5.0, 0.012),
    ]

    for height, alpha in haze_layers:
        haze_values = [
            min(100, value + height)
            for value in smooth_values
        ]

        haze_shape = make_cloud_shape(
            days,
            haze_values,
        )

        haze = PathPatch(
            haze_shape,
            facecolor=cloud_white,
            edgecolor="none",
            alpha=alpha,
            zorder=2.5,
        )

        ax.add_patch(haze)

    # ---------------------------------------------------------
    # Axes
    # ---------------------------------------------------------

    ax.set_xlim(1, len(days))
    ax.set_ylim(0, 100)

    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel(
        "Daily mean cloud amount (%)",
        color=text_blue,
    )

    # Month positions.
    month_days = [
        1,
        32,
        60,
        91,
        121,
        152,
        182,
        213,
    ]

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

    ax.set_xlabel(
        "2026",
        color=text_blue,
    )

    # ---------------------------------------------------------
    # Reference grid
    # ---------------------------------------------------------

    ax.grid(
        axis="y",
        color="white",
        linewidth=0.8,
        alpha=0.65,
    )

    ax.set_axisbelow(True)

    # ---------------------------------------------------------
    # Minimal frame
    # ---------------------------------------------------------

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.spines["left"].set_color(axis_blue)
    ax.spines["bottom"].set_color(axis_blue)

    ax.tick_params(
        axis="both",
        colors=text_blue,
        length=0,
    )

    # ---------------------------------------------------------
    # Title
    # ---------------------------------------------------------

    fig.text(
        0.075,
        0.925,
        "Cloud Cover — Hong Kong, 2026",
        fontsize=18,
        color="#263F4A",
        ha="left",
        va="top",
    )

    # ---------------------------------------------------------
    # Explanation
    # ---------------------------------------------------------

    fig.text(
        0.075,
        0.095,
        "Cloud layer follows the 7-day average of daily cloud amount.",
        fontsize=9,
        color=text_blue,
        alpha=0.9,
        ha="left",
        va="center",
    )

    # ---------------------------------------------------------
    # Source
    # ---------------------------------------------------------

    fig.text(
        0.985,
        0.095,
        "Source: Hong Kong Observatory",
        fontsize=9,
        color=text_blue,
        alpha=0.9,
        ha="right",
        va="center",
    )

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    OUT.mkdir(exist_ok=True)

    fig.savefig(
        OUT / PICTURE,
        dpi=200,
        facecolor=sky_bottom,
    )

    print(f"saved out/{PICTURE}")

    plt.show()


if __name__ == "__main__":
    main()
