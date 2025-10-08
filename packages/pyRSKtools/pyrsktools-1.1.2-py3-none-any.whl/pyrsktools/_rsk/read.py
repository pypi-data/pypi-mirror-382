#!/usr/bin/env python3
# Standard/external imports
from __future__ import annotations
import builtins
from typing import *
import os
import sqlite3
import csv
import numpy as np
import numpy.ma as ma
import numpy.typing as npt
import sys
from enum import IntEnum
import re

# Module imports
from pyrsktools.readers import load_reader, RSKEPDesktopReader
from pyrsktools.datatypes import *
from pyrsktools.utils import rsktime2datetime, formatchannelname
from pyrsktools.channels import *

if TYPE_CHECKING:
    from pyrsktools import RSK


def open(self: RSK) -> None:
    """Open an RBR RSK file and read any available metadata.

    Makes a connection to an RSK (SQLite format) database as obtained
    from an RBR data logger and reads in the instrument's metadata. It populates
    the current instance with the metadata.

    Example:

    >>> rsk = RSK("example.rsk", readHiddenChannels=True)
    ... rsk.open()

    This method is automatically invoked when using the RSK class context manager:

    >>> with RSK("example.rsk") as rsk:
    ...    # RSK is open here
    """
    # Check if the file exists
    if not os.path.isfile(self.filename):
        raise OSError(f"RSK file '{self.filename}' does not exist")
    # Check if we have read permissions on the existing file
    if not os.access(self.filename, os.R_OK):
        raise IOError(f"RSK file '{self.filename}' does not have read permissions")

    # Open the RSK (sqlite3) file
    self._db = sqlite3.connect(f"file:{self.filename}?mode=ro", uri=True)
    # Get the correct reader for the current RSK type/version
    self.dbInfo, self._reader = load_reader(self._db)
    # Load appropriate data attributes.
    # These are typically referred to as the "metadata" of an RSK.
    self.instrument = self._reader.instrument()
    self.deployment = self._reader.deployment()
    self.channels = self._reader.channels()
    self.epoch = self._reader.epoch()
    self.schedule = self._reader.schedule()
    self.scheduleInfo = self._reader.scheduleInfo(self.schedule)
    self.calibrations = self._reader.calibrations()
    self.power = self._reader.power()
    self.parameters = self._reader.parameters()
    self.parameterKeys = self._reader.parameterKeys()
    self.appSettings = self._reader.appSettings()
    self.ranging = self._reader.ranging()
    self.regions = self._reader.regions()
    self.instrumentChannels = self._reader.instrumentChannels()
    self.instrumentSensors = self._reader.instrumentSensors()
    self.diagnosticsChannels = self._reader.diagnosticsChannels()
    self.diagnosticsData = self._reader.diagnosticsData()
    self.geoData = self._reader.geoData()

    isCoda = "RBRcoda" in self.instrument.model
    isBPR = "RBRquartz" in self.instrument.model
    if not isinstance(self._reader, RSKEPDesktopReader) and not isCoda:
        channelStatus = {c.channelID: c.channelStatus for c in self.instrumentChannels}
        toDelete = []
        for channel in self.channels:
            if channel.channelID not in channelStatus:
                continue

            isStored = False if channelStatus[channel.channelID] & 0x04 else True
            isHidden = True if channelStatus[channel.channelID] & 0x01 else False
            isStreamed = False if channelStatus[channel.channelID] & 0x08 else True

            if self._readHiddenChannels:
                if not isBPR and not isStored:
                    toDelete.append(channel.channelID)
                else:
                    if not isStreamed and not isStored:  # e.g., status == 12
                        toDelete.append(channel.channelID)
            else:
                if not isStored or isHidden:
                    toDelete.append(channel.channelID)

        if len(toDelete) > 0:
            self.channels = [c for c in self.channels if c.channelID not in toDelete]
            self.instrumentChannels = [
                c for c in self.instrumentChannels if c.channelID not in toDelete
            ]

    self.appendlog(f"{self.filename} opened using pyRSKtools v{self.version}.")


def _databaseisopenorerror(rsk: RSK) -> None:
    if rsk._db is None:
        raise ConnectionError("Current RSK instance has no database instance.")
    if rsk._reader is None:
        raise ConnectionError("Current RSK instance has no reader instance.")

    try:
        rsk._db.cursor()
    except Exception as ex:
        raise ConnectionError(
            "Failed to connect to database. Please call RSK.open() then try again."
        )


def readdata(
    self: RSK, t1: Optional[np.datetime64] = None, t2: Optional[np.datetime64] = None
) -> None:
    """Read data of an opened RSK file.

    Args:
        t1 (np.datetime64, optional): start time for the range of data to be read. Defaults to None.
        t2 (np.datetime64, optional): end time for the range of data to be read. Defaults to None.

    Retrieves data values from the .rsk file and populates :obj:`RSK.data`.
    If :obj:`RSK.data` already contains data, the newly queried data replaces anything in :obj:`RSK.data`.

    If you would like to read in only a subsection of the database, the ``t1`` and ``t2`` arguments can be used
    to enter start and end times in the form of a NumPY datetime64 object.

    Example:

    >>> rsk.readdata()
    ... # Optional arguments
    ... tstart = np.datetime64("2022-05-03")
    ... tend = np.datetime64("2022-05-04")
    ... rsk.readdata(tstart, tend)
    """
    _databaseisopenorerror(self)

    if not t1:
        t1 = self.epoch.startTime
    if not t2:
        t2 = self.epoch.endTime

    if t2 <= t1:
        raise ValueError("The end time (t2) must be greater (later) than the start time (t1).")

    self.data = self._reader.data(self.channels, t1, t2)


class EventType(IntEnum):
    NOTHING = 0  # nothing new or unknown
    DOWN = 1  # downcast (descending)
    UP = 2  # upcast (ascending)
    OUT = 3  # out of water


def _detectprofiles(
    pressure: npt.NDArray[np.float64],
    timestamp: npt.NDArray[np.datetime64],
    conductivity: npt.NDArray[np.float64],
    pressureThreshold: float = 3.0,
    conductivityThreshold: float = 0.05,
) -> npt.NDArray:
    indx = ~(np.isnan(pressure) | np.isnan(conductivity))
    pressure = pressure[indx]
    conductivity = conductivity[indx]
    timestamp = timestamp[indx]

    pressureThreshold = float(pressureThreshold)
    conductivityThreshold = float(conductivityThreshold)
    # Event profiles. Timestamp and event index describing the start of the event
    # (1 = downcast, 2 = upcast, 3 = out of water)
    events: List[Tuple[np.datetime64, EventType]] = []
    detectcaststate = EventType.NOTHING
    hasC = conductivity.size > 0
    klast = 0
    maxpressure = pressure[0]
    minpressure = pressure[0]

    for k in range(len(timestamp)):
        event = EventType.NOTHING

        if hasC and conductivity[k] < conductivityThreshold:
            event = EventType.OUT
            minpressure = pressure[k]
        else:
            if detectcaststate == EventType.NOTHING:  # unknown
                if pressure[k] > maxpressure:
                    maxpressure = pressure[k]
                    if (maxpressure - minpressure) > pressureThreshold:
                        detectcaststate = EventType.DOWN
                        event = EventType.DOWN

                if pressure[k] < minpressure:
                    minpressure = pressure[k]
                    if (maxpressure - minpressure) > pressureThreshold:
                        detectcaststate = EventType.UP
                        event = EventType.UP

            elif detectcaststate == EventType.DOWN:  # down
                if pressure[k] > maxpressure:
                    maxpressure = pressure[k]

                if pressure[k] < minpressure:
                    minpressure = pressure[k]

                # If true, we are going up, as set by the profile detection algorithm
                if maxpressure - pressure[k] > max(
                    pressureThreshold, 0.05 * (maxpressure - minpressure)
                ):
                    detectcaststate = EventType.UP
                    event = EventType.UP
                    minpressure = pressure[k]
                else:
                    detectcaststate = EventType.DOWN

            elif detectcaststate == EventType.UP:  # up
                if pressure[k] > maxpressure:
                    maxpressure = pressure[k]

                if pressure[k] < minpressure:
                    minpressure = pressure[k]

                # If true, we are going down, as set by the profile detection algorithm
                if pressure[k] - minpressure > max(
                    pressureThreshold, 0.05 * (maxpressure - minpressure)
                ):
                    detectcaststate = EventType.DOWN
                    event = EventType.DOWN
                    maxpressure = pressure[k]
                else:
                    detectcaststate = EventType.UP

        tstamp = None
        if event == EventType.DOWN:  # downcast
            profiletime = timestamp[klast:k]
            idx = np.flatnonzero(pressure[klast:k] == minpressure)[-1]
            events.append((profiletime[idx], event))
            klast = k
        elif event == EventType.UP:  # upcast
            profiletime = timestamp[klast:k]
            idx = np.flatnonzero(pressure[klast:k] == maxpressure)[-1]
            events.append((profiletime[idx], event))
            klast = k
        elif event == EventType.OUT:  # out of water
            if len(events) == 0 or events[-1][1] != EventType.OUT:
                events.append((timestamp[k], event))
                klast = k

    return np.array(events, dtype=[("time", "datetime64[ms]"), ("type", "uint8")])


def computeprofiles(
    self: RSK, pressureThreshold: float = 3.0, conductivityThreshold: float = 0.05
) -> None:
    """Compute profiles in a time series using pressure and conductivity data (if it exists).

    Args:
        pressureThreshold (float, optional): pressure threshold. Defaults to 3.0.
        conductivityThreshold (float, optional): conductivity threshold. Defaults to 0.05.

    Detects profiles using the pressure channel in the RSK and populates :obj:`RSK.regions`
    with the produced metadata.

    The algorithm runs through the pressure data of the RSK and finds instances of a pressure reversal
    that is greater than ``pressureThreshold`` or 5% of the pressure differential of the last profile (whichever is greater).
    If it detects a pressure reversal it goes back to find the minimum or maximum pressure since the last event and records
    it as the beginning of the upcast or downcast, depending on the direction of the reversal.

    When a conductivity channel is available, the algorithm records the samples where the conductivity is less than
    ``conductivityThreshold`` as out of the water and excludes them from the cast.

    The default ``pressureThreshold`` of 3 dbar may be too large for short profiles.
    Consider using one-quarter of the pressure range as a guideline, (max(Pressure) - min(Pressure)) * 1/4.

    Example:

    >>> rsk.computeprofiles()
    ... # Optional arguments
    ... rsk.computeprofiles(pressureThreshold=5.0, conductivityThreshold=0.06)

    This next example illustrates how to use this method in combination with :func:`RSK.getprofilesindices`
    to parse a time series of data into individual upcasts and downcasts.

    >>> with RSK("example.rsk") as rsk:
    ...     rsk.readdata()
    ...     print(rsk)
    ...     # RSK
    ...     # ...
    ...     #   .regions is unpopulated
    ...     # ...
    ...     rsk.computeprofiles()
    ...     print(rsk)
    ...     # RSK
    ...     # ...
    ...     #   .regions is populated with 45 elements
    ...     # ...
    ...     upcastIndices = rsk.getprofilesindices(direction="up")
    ...     downcastIndices = rsk.getprofilesindices(direction="down")
    """
    self.dataexistsorerror()

    data = self.data

    timestamp = data["timestamp"]
    if Pressure.longName in data.dtype.names:
        pressure = data[Pressure.longName]
    elif SeaPressure.longName in data.dtype.names:
        pressure = data[SeaPressure.longName]
    else:
        raise ValueError(
            f"Data does not contain '{Pressure.longName}' or '{SeaPressure.longName}' channels"
        )

    # If conductivity is present, it will be used to detect
    # when the logger is out of the water.
    if Conductivity.longName in data.dtype.names:
        conductivity = data[Conductivity.longName]
    else:
        conductivity = np.array([])

    # Detect profile events (e.g., 3 = regions of out of water, 2 = upcast, or 1 = downcast)
    # Contains rows of: [tstamp, event], where 'event' is 3, 2, or 1
    events = _detectprofiles(
        pressure, timestamp, conductivity, pressureThreshold, conductivityThreshold
    )

    # If there is at least one upcast and downcast pair, we can create our profiles
    if EventType.DOWN in events["type"] and EventType.UP in events["type"]:
        hasProfile = True
        # Reset regions, i.e., remove those loaded from the RSK, so we can generate our own below
        self.printwarning(
            "Ruskin profile and cast annotations will be deleted as they might conflict with the new profiles detected"
        )
        previousNonProfileRegions = [
            r
            for r in self.regions
            if not (isinstance(r, RegionCast) or isinstance(r, RegionProfile))
        ]
        self.regions = []
    else:
        hasProfile = False
        self.printwarning("No profiles were detected in this dataset with the given parameters.")
        return

    # Use the events to establish profile start and end times.
    # Event number 1 is a downcast start
    downstart = events["time"][np.flatnonzero(events["type"] == EventType.DOWN)]
    downend = np.full(downstart.size, np.nan, dtype=downstart.dtype)
    # Event number 2 is a upcast start
    upstart = events["time"][np.flatnonzero(events["type"] == EventType.UP)]
    upend = np.full(upstart.size, np.nan, dtype=upstart.dtype)

    assert downstart.size == downend.size
    assert upstart.size == upend.size

    u = 0  # up index
    d = 0  # down index
    for i in range(1, len(events)):
        t = np.flatnonzero(timestamp == events[i]["time"])[-1]

        if events[i - 1]["type"] != EventType.OUT:
            if events[i]["type"] == EventType.DOWN:
                # Upcast end is the sample of a downcast start
                upend[u] = timestamp[t]
                u += 1
            elif events[i]["type"] == EventType.UP:
                # Downcast end is the sample of a upcast start
                downend[d] = timestamp[t]
                d += 1

        if events[i]["type"] == EventType.OUT:
            if events[i - 1]["type"] == EventType.DOWN:
                # Event 3 ends a downcast if that was the last event
                downend[d] = timestamp[t]
                d += 1
            elif events[i - 1]["type"] == EventType.UP:
                # Event 3 ends a upcast if that was the last event
                upend[u] = timestamp[t]
                u += 1

    # Finish the last profile
    if events["type"][-1] == EventType.DOWN:
        downend[-1] = timestamp[-1]
    elif events["type"][-1] == EventType.UP:
        upend[-1] = timestamp[-1]

    profilesMax = max(upstart.size, downstart.size)
    profilesMin = min(upstart.size, downstart.size)
    # Types for computational attributes
    profiles = np.full(
        profilesMax,
        np.nan,
        dtype=[
            ("upcast", [("tstart", "datetime64[ms]"), ("tend", "datetime64[ms]")]),
            ("downcast", [("tstart", "datetime64[ms]"), ("tend", "datetime64[ms]")]),
        ],
    )
    profiles["upcast"]["tstart"][: upstart.size] = upstart
    profiles["upcast"]["tend"][: upend.size] = upend
    profiles["downcast"]["tstart"][: downstart.size] = downstart
    profiles["downcast"]["tend"][: downend.size] = downend

    if upstart[0] > downstart[0]:
        firstdir, lastdir = profiles["downcast"], profiles["upcast"]
        firstType, lastType = "down", "up"
    else:
        firstdir, lastdir = profiles["upcast"], profiles["downcast"]
        firstType, lastType = "up", "down"

    regions = []
    # Populate regions derived from our calculated profiles
    for n in range(profilesMin):
        nprofile = n * 3 - 2

        profileRegion = RegionProfile(
            datasetID=1,
            regionID=nprofile,
            type=self._reader.REGION_TYPE_MAPPING[RegionProfile]["type"],
            tstamp1=firstdir["tstart"][n],
            tstamp2=lastdir["tend"][n],
            label=f"Profile {n}",
            description="pyRSKtools-generated profile",
            collapsed=False,
        )
        firstcastRegion = RegionCast(
            datasetID=1,
            regionID=nprofile + 1,
            type=self._reader.REGION_TYPE_MAPPING[RegionCast]["type"],
            tstamp1=firstdir["tstart"][n],
            tstamp2=firstdir["tend"][n],
            label=f"{firstType}cast {n}",
            description="pyRSKtools-generated cast",
            collapsed=False,
            regionProfileID=nprofile,
            regionType=firstType.upper(),
        )
        lastcastRegion = RegionCast(
            datasetID=1,
            regionID=nprofile + 2,
            type=self._reader.REGION_TYPE_MAPPING[RegionCast]["type"],
            tstamp1=lastdir["tstart"][n],
            tstamp2=lastdir["tend"][n],
            label=f"{lastType}cast {n}",
            description="pyRSKtools-generated cast",
            collapsed=False,
            regionProfileID=nprofile,
            regionType=lastType.upper(),
        )

        regions.extend([profileRegion, firstcastRegion, lastcastRegion])

    # If there is unequal number of upcasts and downcasts,
    # add the last one single cast
    if upstart.size != downstart.size:
        n = profilesMax - 1
        nprofile = n * 3 - 2

        profileRegion = RegionProfile(
            datasetID=1,
            regionID=nprofile,
            type=self._reader.REGION_TYPE_MAPPING[RegionProfile]["type"],
            tstamp1=firstdir["tstart"][n],
            tstamp2=firstdir["tend"][n],
            label=f"Profile {n}",
            description="pyRSKtools-generated profile",
            collapsed=False,
        )
        firstcastRegion = RegionCast(
            datasetID=1,
            regionID=nprofile + 1,
            type=self._reader.REGION_TYPE_MAPPING[RegionCast]["type"],
            tstamp1=firstdir["tstart"][n],
            tstamp2=firstdir["tend"][n],
            label=f"{firstType}cast {n}",
            description="pyRSKtools-generated cast",
            collapsed=False,
            regionProfileID=nprofile,
            regionType=firstType.upper(),
        )

        regions.extend([profileRegion, firstcastRegion])

    self.regions = previousNonProfileRegions + regions


def getprofilesindices(
    self: RSK, profiles: Union[int, Collection[int]] = [], direction: str = "both"
) -> List[List[int]]:
    """Get a list of indices for each profile or cast direction used to index into :obj:`RSK.data`.

    Args:
        profiles (Union[int, Collection[int]], optional): profile number(s) to select. Defaults to [] (all profiles).
        direction (str, optional): cast direction of either "up", "down", or "both". Defaults to "both".

    Returns:
        List[List[int]]: a list of profile/cast indices; each element in the returned list is a list
        itself which may be used to index into :obj:`RSK.data`.

    This method quickly computes a list (of lists) of indices into :obj:`RSK.data` for each profile/cast
    using the metadata in :obj:`RSK.regions`.

    Example:

    >>> profileIndices = rsk.getprofilesindices()
    ... upcastIndices = rsk.getprofilesindices(direction="up")
    ... firstDowncastIndices = rsk.getprofilesindices(profiles=1, direction="down")
    """
    if profiles is None:
        raise TypeError("Type of 'None' invalid. Use an empty list ([]) to select all profiles.")

    if not self.regions:
        raise ValueError(
            "No profile regions in the current RSK instance. Please see rsk.computeprofiles()."
        )

    if self.data.size == 0:
        raise ValueError("No data in the current RSK instance")

    profileRegions = self.getprofilesorerror(profiles)

    # The way the profiles are selected below is a bit odd, sorry.
    # The above profileRegions retrieved above is a tuple of
    # (RegionCast, RegionCast, RegionProfile), each of
    # which have tstamp1 and tstamp2 marking their start and end
    # respectively. However, when the user specifies "both" we
    # get into a weird case where the last point of the first cast
    # and the first point of the second cast are the same (and we want to
    # count them both). So, for "both" we use the individual cast
    # regions instead of the profile region to make sure we double count.
    # Below I just encode the direction into an int so it might be
    # quicker to compare later.
    if direction == "down":
        regionIndex = 0 if profileRegions[0][0].isdowncast() else 1
    elif direction == "up":
        regionIndex = 1 if profileRegions[0][1].isupcast() else 0
    else:
        regionIndex = 2

    # Here we get the actual profile indices (accounting for double
    # counted points when direction is "both")
    profileDataIndices = []
    for p in profileRegions[:-1]:
        if regionIndex == 2:
            # No matter downcast comes first or upcast, the cast with smaller tstamp1 should be listed first
            firstCast, secondCast = [0, 1] if p[0].tstamp1 < p[1].tstamp1 else [1, 0]
            indices = np.flatnonzero(
                np.logical_and(
                    self.data["timestamp"] >= p[firstCast].tstamp1,
                    self.data["timestamp"] <= p[firstCast].tstamp2,
                )
            )
            indices = np.concatenate(
                (
                    indices,
                    np.flatnonzero(
                        np.logical_and(
                            self.data["timestamp"] >= p[secondCast].tstamp1,
                            self.data["timestamp"] <= p[secondCast].tstamp2,
                        )
                    ),
                )
            )
        else:
            indices = np.flatnonzero(
                np.logical_and(
                    self.data["timestamp"] >= p[regionIndex].tstamp1,
                    self.data["timestamp"] <= p[regionIndex].tstamp2,
                )
            )

        profileDataIndices.append(indices.tolist())

    # deal with the last profile separately, it could contain a pair of casts or single cast
    p = profileRegions[-1]
    if None in p:  # unequal number of up and downcast
        p = list(p)
        p.remove(None)
        if (
            (regionIndex == 2)
            or (profileRegions[0][0].isdowncast() and direction == "down")
            or (profileRegions[0][0].isupcast() and direction == "up")
        ):
            indices = np.flatnonzero(
                np.logical_and(
                    self.data["timestamp"] >= p[0].tstamp1,
                    self.data["timestamp"] <= p[0].tstamp2,
                )
            )
            profileDataIndices.append(indices.tolist())
    else:  # paired casts
        if regionIndex == 2:
            # No matter downcast comes first or upcast, the cast with smaller tstamp1 should be listed first
            firstCast, secondCast = [0, 1] if p[0].tstamp1 < p[1].tstamp1 else [1, 0]
            indices = np.flatnonzero(
                np.logical_and(
                    self.data["timestamp"] >= p[firstCast].tstamp1,
                    self.data["timestamp"] <= p[firstCast].tstamp2,
                )
            )
            indices = np.concatenate(
                (
                    indices,
                    np.flatnonzero(
                        np.logical_and(
                            self.data["timestamp"] >= p[secondCast].tstamp1,
                            self.data["timestamp"] <= p[secondCast].tstamp2,
                        )
                    ),
                )
            )
        else:
            indices = np.flatnonzero(
                np.logical_and(
                    self.data["timestamp"] >= p[regionIndex].tstamp1,
                    self.data["timestamp"] <= p[regionIndex].tstamp2,
                )
            )

        profileDataIndices.append(indices.tolist())

    return profileDataIndices


def getprofilesindicessortedbycast(
    self: RSK, profiles: Union[int, Collection[int]] = [], direction: str = "both"
) -> List[List[int]]:
    """Get a list of indices for each cast direction used to index into :obj:`RSK.data`.

    Args:
        profiles (Union[int, Collection[int]], optional): profile number(s) to select. Defaults to [] (all profiles).
        direction (str, optional): cast direction of either "up", "down", or "both". Defaults to "both".

    Returns:
        List[List[int]]: a list of cast indices; each element in the returned list is a list
        itself which may be used to index into :obj:`RSK.data`.

    This method quickly computes a list (of lists) of indices into :obj:`RSK.data` for each profile/cast
    using the metadata in :obj:`RSK.regions`.

    Example:

    >>> allcastIndices = rsk.getprofilesindicessortedbycast()
    """
    if profiles is None:
        raise TypeError("Type of 'None' invalid. Use an empty list ([]) to select all profiles.")

    if not self.regions:
        raise ValueError(
            "No profile regions in the current RSK instance. Please see rsk.computeprofiles()."
        )

    if self.data.size == 0:
        raise ValueError("No data in the current RSK instance")

    profileRegions = self.getprofilesorerror(profiles)
    if direction == "both":
        up = self.getprofilesindices(profiles, "up")
        down = self.getprofilesindices(profiles, "down")
        indices_bycasts = []

        for i in range(min(len(up), len(down))):
            if profileRegions[0][0].isdowncast():
                indices_bycasts.append(down[i])
                indices_bycasts.append(up[i])
            else:
                indices_bycasts.append(up[i])
                indices_bycasts.append(down[i])

        if len(up) != len(down):
            lastprofile: list = up[-1] if len(up) > len(down) else down[-1]
            indices_bycasts.append(lastprofile)
    else:
        indices_bycasts = self.getprofilesindices(profiles, direction)

    return indices_bycasts


def getdataseriesindices(self: RSK) -> List[List[int]]:
    """Get a list of all the indices of :obj:`RSK.data`.

    Returns:
        List[List[int]]: a list of indices for the whole data series; the first element of the returned list
        contains the list used to index into :obj:`RSK.data`. The nested list provides output compatible with
        the same uses cases of :meth:`RSK.getprofilesindices`.

    Example:

    >>> dataSeriesIndices = rsk.getdataseriesindices()

    """
    indices = np.flatnonzero(
        np.logical_and(
            self.data["timestamp"] >= self.epoch.startTime,
            self.data["timestamp"] <= self.epoch.endTime,
        )
    ).tolist()

    return [indices]


def readprocesseddata(
    self: RSK, t1: Optional[np.datetime64] = None, t2: Optional[np.datetime64] = None
) -> None:
    """Read the burst data of an opened RSK file.

    Args:
        t1 (np.datetime64, optional): start time for a range of burst data to be read. Defaults to None.
        t2 (np.datetime64, optional): end time for a range of burst data to be read. Defaults to None.

    This function reads all or a subset (determined by t1 and t2) of the burst data and writes it
    to the :obj:`RSK.processedData` variable of this instance.

    When a dataset has burst data, the raw high-frequency values reside in the :obj:`RSK.processedData` field.
    This field is composed of one sample for each burst with a timestamp set to be the first value of each burst period;
    the sample is the average of the values during the corresponding burst.

    Example:

    >>> rsk.readprocesseddata()
    ... # Optional arguments
    ... tstart = np.datetime64("2022-05-03")
    ... tend = np.datetime64("2022-05-04")
    ... rsk.readprocesseddata(tstart, tend)
    """
    _databaseisopenorerror(self)
    if not t1:
        t1 = self.epoch.startTime
    if not t2:
        t2 = self.epoch.endTime

    if t2 <= t1:
        raise ValueError("The end time (t2) must be greater (later) than the start time (t1).")

    self.processedData = self._reader.processedData(self.channels, t1, t2)


def csv2rsk(
    cls: Type[RSK],
    fname: str,
    model: str = "unknown",
    serialID: int = 0,
    firmwareVersion: str = "NA",
    firmwareType: int = 103,
    partNumber: str = "unknown",
) -> RSK:
    """Convert a CSV file into an :class:`RSK` class instance.

    Args:
        fname (str): name of the CSV file
        model (str, optional):  instrument model from which data was collected. Defaults to "unknown".
        serialID (int, optional): serial ID of the instrument. Defaults to 0.
        firmwareVersion (str, optional): firmware version of the instrument, e.g., 1.135. Defaults to "NA".
        firmwareType(int, optional): firmware type of the instrument, e.g., 103. Defaults to 103.
        partNumber (str, optional):  instrument part number. Defaults to "unknown".

    Returns:
        RSK: :class:`RSK` class instance populated with the given CSV data.

    The function reads in a CSV file and creates an :class:`RSK` class instance. The header of
    the CSV file must follow exactly the format below to make the function work:

        | "timestamp (ms)","conductivity (mS/cm)","temperature (°C)","pressure (dbar)"
        | 1564099200000,49.5392,21.8148,95.387
        | 1564099200167,49.5725,21.8453,95.311
        | 1564099200333,49.5948,21.8752,95.237

    where the first column represents the timestamp, which is milliseconds elapsed since Jan 1 1970
    (i.e. UNIX time or POSIX time). The header for each column is comprised with channel name followed by
    space and unit (with parentheses) with double quotes.

    Example:

    >>> rsk = RSK.csv2rsk("example.csv")
    ... # Optional arguments
    ... rsk = RSK.csv2rsk("example.csv", model="RBRconcerto", serialID=200004)
    """
    # Have to use builtins here because we defined an `open()` method above
    with builtins.open(fname, "r", newline="") as f:
        reader = csv.reader(f, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
        header = next(reader)

        if "time" not in header[0].lower():
            raise ValueError(f'Expected CSV column 0 ("{header[0]}") to have name "timestamp"')

        rsk = cls(fname)
        types = [("timestamp", "datetime64[ms]")]
        channelNames = {}  # Keep track of how many times we have hit a specific channel name
        channelRegex = re.compile(r"(.*)\s+\((.*)\)")
        for i, channelInfo in enumerate(header[1:]):
            if match := channelRegex.match(channelInfo):
                dbName = match.group(1)
                channelName = formatchannelname(dbName)
                units = match.group(2)
            else:
                raise ValueError(f"Encountered invalid column name format: {channelInfo}")

            if channelName not in channelNames:
                channelNames[channelName] = 0
            else:
                channelNames[channelName] += 1
                channelName = f"{channelName}{channelNames[channelName]}"

            rsk.channels.append(
                Channel(
                    channelID=i + 1,
                    shortName=channelName,
                    longName=channelName,
                    units=units,
                    _dbName=dbName,
                )
            )

            types.append((channelName, "float64"))

        rsk.data = np.fromiter(((rsktime2datetime(int(r[0])), *r[1:]) for r in reader), dtype=types)
        rsk.dbInfo = DbInfo(
            version=RSKEPDesktopReader.MAX_SUPPORTED_SEMVER,
            type=RSKEPDesktopReader.TYPE,
        )
        rsk.instrument = Instrument(
            instrumentID=1,
            model=model,
            firmwareVersion=firmwareVersion,
            firmwareType=firmwareType,
            partNumber=partNumber,
        )
        rsk.deployment = Deployment(
            deploymentID=1,
            instrumentID=1,
            comment="",
            loggerStatus=None,
            loggerTimeDrift=None,
            timeOfDownload=np.datetime64("now", "ms"),
            name=fname,
            sampleSize=None,
        )
        rsk.epoch = Epoch(
            deploymentID=1,
            startTime=np.min(rsk.data["timestamp"]),
            endTime=np.max(rsk.data["timestamp"]),
        )
        return rsk


def close(self: RSK) -> None:
    """Closes the connection made to the RSK (SQLite format) database.

    Example:

    >>> rsk.close()

    NOTE: This method is automatically invoked when using the context manager approach.
    """
    if self._db:
        self._db.close()
        self._db = None
        self._reader = None
