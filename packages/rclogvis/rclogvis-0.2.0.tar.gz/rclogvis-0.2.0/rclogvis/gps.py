#
#   2025 Fabian Jankowski
#   GPS related functions.
#

import gpxpy.gpx
import pandas as pd
from xml.etree import ElementTree


def create_gpx_file(df):
    gpx = gpxpy.gpx.GPX()
    gpx.name = "GPS Data Export"
    gpx.description = "Export of the RC GPS data"
    gpx.time = pd.Timestamp.utcnow().round("s")

    # add extension namespace
    gpx.nsmap["gpxtpx"] = "http://www.garmin.com/xmlschemas/TrackPointExtension/v2"

    # track
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx_track.name = "Track"
    gpx.tracks.append(gpx_track)

    # segment
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    # date conversion
    _timestamps = df["datetime"].dt.tz_convert("UTC")
    _timestamps = _timestamps.dt.round("s")

    # km/h -> m/s
    _speeds = df["GSpd(kmh)"] / 3.6

    # track points
    for i in range(len(df.index)):
        _point = gpxpy.gpx.GPXTrackPoint(
            df["latitude"].iloc[i],
            df["longitude"].iloc[i],
            elevation=df["Alt(m)"].iloc[i],
            time=_timestamps.iloc[i],
        )
        _point.satellites = df["Sats"].iloc[i]

        # add speed extension
        _speed = _speeds.iloc[i]
        _extension = ElementTree.fromstring(
            f"""<gpxtpx:TrackPointExtension xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v2">
            <gpxtpx:speed>{_speed:.1f}</gpxtpx:speed>
            </gpxtpx:TrackPointExtension>
        """
        )
        _point.extensions.append(_extension)

        gpx_segment.points.append(_point)

    with open("export.gpx", "w") as fd:
        fd.write(gpx.to_xml(version="1.1"))


def get_distances(df):
    gpx = gpxpy.gpx.GPX()

    # track
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    # segment
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    # track points
    for i in range(len(df.index)):
        _point = gpxpy.gpx.GPXTrackPoint(
            df["latitude"].iloc[i],
            df["longitude"].iloc[i],
            elevation=df["Alt(m)"].iloc[i],
        )

        gpx_segment.points.append(_point)

    # cumulative distance travelled
    _data = gpx.get_points_data()
    cum_dists = [item.distance_from_start for item in _data]

    # distance from home
    # XXX: maybe average the first X points here
    _start = next(gpx.walk(only_points=True))
    home_dists = [item.distance_3d(_start) for item in gpx.walk(only_points=True)]

    return cum_dists, home_dists
