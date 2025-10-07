#
#   2025 Fabian Jankowski
#   Plotting related functions.
#

import matplotlib
from matplotlib.collections import LineCollection
from matplotlib.patches import FancyArrowPatch
import matplotlib.pyplot as plt
import numpy as np


def use_custom_matplotlib_formatting():
    """
    Adjust the matplotlib configuration parameters for custom format.
    """

    matplotlib.rcParams["font.family"] = "sans"
    matplotlib.rcParams["font.size"] = 12.0
    matplotlib.rcParams["lines.markersize"] = 8
    matplotlib.rcParams["legend.frameon"] = False
    # make tickmarks more visible
    matplotlib.rcParams["xtick.major.size"] = 6
    matplotlib.rcParams["xtick.major.width"] = 1.5
    matplotlib.rcParams["xtick.minor.size"] = 4
    matplotlib.rcParams["xtick.minor.width"] = 1.5
    matplotlib.rcParams["ytick.major.size"] = 6
    matplotlib.rcParams["ytick.major.width"] = 1.5
    matplotlib.rcParams["ytick.minor.size"] = 4
    matplotlib.rcParams["ytick.minor.width"] = 1.5


def plot_time_series(df, fields, title=""):
    figsize = (6.4, 7.0)
    fig, axs = plt.subplots(figsize=figsize, nrows=len(fields), sharex=True)

    for i, _label in enumerate(fields):
        axs[i].plot(df["flighttime"], df[_label])
        axs[i].grid()

        _nice_label = _label.replace("(", "\n(")
        axs[i].set_ylabel(_nice_label)

    lastax = axs[len(fields) - 1]
    lastax.set_xlabel("Flight time (min)")

    fig.suptitle(title)

    fig.align_ylabels()
    fig.tight_layout()


def plot_gps_trajectory(df):
    x = (df["longitude"] - df["longitude"].iat[0]).values
    y = (df["latitude"] - df["latitude"].iat[0]).values

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    norm = plt.Normalize(df["Alt(m)"].min(), df["Alt(m)"].max())

    lc = LineCollection(segments, cmap="viridis", norm=norm)
    lc.set_array(df["Alt(m)"].astype(float).values)
    lc.set_linewidth(2)
    lc.set_zorder(5)

    fig = plt.figure()
    ax = fig.add_subplot()

    ax.add_collection(lc)

    for i in range(0, len(x) - 1, 7):
        arrow = FancyArrowPatch(
            (x[i], y[i]),
            (x[i + 1], y[i + 1]),
            mutation_scale=20,
            arrowstyle="->",
            color="tab:blue",
            zorder=4,
        )
        ax.add_patch(arrow)

    # home point
    ax.scatter(
        0,
        0,
        s=260,
        marker="o",
        facecolor="none",
        edgecolor="tab:red",
        zorder=2,
    )
    ax.text(
        0,
        0,
        "H",
        color="tab:red",
        verticalalignment="center",
        horizontalalignment="center",
        zorder=3,
    )

    plt.colorbar(lc, ax=ax, label="Altitude (m)")

    ax.set_xlabel("Longitude (deg)")
    ax.set_ylabel("Latitude (deg)")

    # set visible area
    thresh = 0.002
    xmin = np.minimum(-thresh, 1.2 * x.min())
    xmax = np.maximum(thresh, 1.2 * x.max())
    ymin = np.minimum(-thresh, 1.2 * y.min())
    ymax = np.maximum(thresh, 1.2 * y.max())

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    fig.tight_layout()


def plot_histograms(df, fields, title=""):
    figsize = (6.4, 7.0)
    fig, axs = plt.subplots(figsize=figsize, nrows=len(fields))

    for i, _label in enumerate(fields):
        axs[i].hist(
            df[_label], bins="auto", density=True, histtype="step", lw=2, zorder=3
        )
        axs[i].grid()

        axs[i].axvline(x=df[_label].median(), color="C1", ls="dashed", lw=2, zorder=4)

        _nice_label = _label.replace("(", " (")
        axs[i].set_xlabel(_nice_label)
        axs[i].set_ylabel("PDF")

    fig.suptitle(title)

    fig.align_ylabels()
    fig.tight_layout()
