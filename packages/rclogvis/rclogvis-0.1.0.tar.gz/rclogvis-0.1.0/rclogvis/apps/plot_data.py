#
#   2025 Fabian Jankowski
#   Plot telemetry log data.
#

import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from rclogvis.gps import create_gpx_file
from rclogvis.plotting import (
    use_custom_matplotlib_formatting,
    plot_time_series,
    plot_gps_trajectory,
    plot_histograms,
)


def parse_args():
    """
    Parse the commandline arguments.

    Returns
    -------
    args: populated namespace
        The commandline arguments.
    """

    parser = argparse.ArgumentParser(
        description="Plot telemetry log data.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("filename", type=str, help="Filename to process.")

    args = parser.parse_args()

    return args


#
# MAIN
#


def main():
    # handle command line arguments
    args = parse_args()

    use_custom_matplotlib_formatting()

    df = pd.read_csv(args.filename)

    print(df.columns)

    df["datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
    # localise
    # XXX: we must change this depending on actual local timezone
    df["datetime"] = df["datetime"].dt.tz_localize("Europe/Paris")
    df["flighttime"] = (
        df["datetime"] - df["datetime"].iat[0]
    ).dt.total_seconds() / 60.0

    # convert to degrees
    df["Ptch(deg)"] = df["Ptch(rad)"] * 180.0 / np.pi
    df["Roll(deg)"] = df["Roll(rad)"] * 180.0 / np.pi
    df["Yaw(deg)"] = df["Yaw(rad)"] * 180.0 / np.pi

    # split into latitude and longitude
    df[["latitude", "longitude"]] = df["GPS"].str.split(" ", n=1, expand=True)
    df["latitude"] = pd.to_numeric(df["latitude"])
    df["longitude"] = pd.to_numeric(df["longitude"])

    # control link
    fields = [
        "1RSS(dB)",
        "RQly(%)",
        "RSNR(dB)",
        "TPWR(mW)",
        "TRSS(dB)",
        "TQly(%)",
        "TSNR(dB)",
    ]

    plot_time_series(df, fields, title="Control Link")

    fields = ["1RSS(dB)", "RQly(%)", "RSNR(dB)", "TRSS(dB)"]

    plot_histograms(df, fields, title="Control Link Histograms")

    # battery
    fields = ["RxBt(V)", "Curr(A)", "Capa(mAh)", "Bat%(%)", "FM"]

    plot_time_series(df, fields, title="Battery")

    fields = ["Curr(A)", "Ptch(deg)", "GSpd(kmh)"]

    plot_histograms(df, fields, title="Battery Histograms")

    # gps
    fields = ["GSpd(kmh)", "Hdg(°)", "Alt(m)", "Sats"]

    plot_time_series(df, fields, title="GPS")

    # attitude
    fields = ["Ptch(deg)", "Roll(deg)", "Yaw(deg)"]

    plot_time_series(df, fields, title="Attitude")

    # stick input
    fields = ["Rud", "Ele", "Thr", "Ail"]

    plot_time_series(df, fields, title="Stick input")

    # gps trajectory
    plot_gps_trajectory(df)

    # output gpx file
    create_gpx_file(df)

    plt.show()


if __name__ == "__main__":
    main()
