#!/usr/bin/env python3
# Standard/external imports
from __future__ import annotations
from typing import *
import time
import inspect
from copy import deepcopy
import sqlite3

# Module imports
from pyrsktools.datatypes import *
from pyrsktools import channels as pychannels
from pyrsktools.readers import load_reader, RSKEPDesktopReader
from pyrsktools import __version__ as pyversion
from pyrsktools.utils import formatchannelname
import numpy as np
import numpy.typing as npt

if TYPE_CHECKING:
    from pyrsktools import RSK


def copy(self: RSK) -> RSK:
    """Create a full `deep <https://docs.python.org/3/library/copy.html#copy.deepcopy>`_
    copy of the current :class:`.RSK` instance. The new copy will contain all the data
    of, and be fully independent from, the original.

    Returns:
        RSK: a deep copy of the current :class:`.RSK` instance.
    """
    # Save references to all stateful objects from the current instance
    db = self._db
    reader = self._reader
    # Set all stateful objects of the current instance to None
    self._reader = None
    self._db = None
    # Take a deep copy of the current instance, i.e., create a new copied instance;
    # without any stateful objects
    rskCopy = deepcopy(self)
    # Restore the current instance's stateful objects
    self._db = db
    self._reader = reader
    # Now create new stateful objects for the copied instance
    rskCopy._db = sqlite3.connect(f"file:{self.filename}?mode=ro", uri=True)
    _, rskCopy._reader = load_reader(rskCopy._db)
    # rskCopy is now fully independent from the current instance, i.e.,
    # a full deep copy (with the exception of new instances of the stateful objects)
    return rskCopy


def create(
    cls: Type[RSK],
    timestamps: Collection[np.datetime64],
    values: Collection[Collection[float]],
    channels: Collection[str],
    units: Collection[str],
    filename: str = "sample.rsk",
    model: str = "unknown",
    serialID: int = 0,
) -> RSK:
    """Create an :class:`RSK` instance from given time series data.

    Args:
        timestamps (Collection[np.datetime64]): a 1D array/list of timestamps (np.datetime64 format) of size n
        values (Collection[Collection[float]]): a 2D array/list of data of size [n,m]
        channels (Collection[str]): a 1D array/list of channel names of size m
        units (Collection[str]): a 1D array/list of channel units of size m
        filename (str, optional): filename to give a general description of the data. Defaults to "sample.rsk".
        model (str, optional): instrument model from which data was collected. Defaults to "unknown".
        serialID (int, optional): serial ID of the instrument from which data was collected. Defaults to 0.

    Returns:
        RSK: created :class:`RSK` class instance with given time series data.

    Creates an instance of this class containing data and channels specified by the user.
    For example, the data could originate from a CTD on a profiling float or a glider.
    The data could even come from CTDs from manufacturers.
    The purpose of this function is to allow users to easily apply pyRSKtools post-processing
    and visualization functions to any dataset. It is particularly convenient when one needs to
    compare data measured with an RBR CTD to other sources (e.g., other CTDs or bottle samples).

    Example:

    >>> timestamps = [np.datetime64(1651550400000, "ms"),
    ...               np.datetime64(1651550402000, "ms"),
    ...               np.datetime64(1651550404000, "ms")]
    ... values = [[39.9973,   16.2695,   10.1034],
    ...           [39.9873,   16.2648,   10.1266],
    ...           [39.9887,   16.2553,   10.1247]]
    ... channels = ["conductivity","temperature","pressure"]
    ... units = ["mS/cm","°C","dbar"]
    ... rsk = RSK.create(timestamps=timestamps, values=values, channels=channels, units=units)
    """
    if len(timestamps) == 0 or len(values) == 0 or len(channels) == 0 or len(units) == 0:
        raise ValueError("Argument given with length of zero.")

    n, m = len(timestamps), len(channels)

    if len(units) != m:
        raise ValueError("Argument 'units' has length unequal to argument 'channels'")

    if len(values) != n:
        raise ValueError("Argument 'values' has length unequal to argument 'timetamps'")

    # Create an RSK class instance
    rsk = cls(filename)

    # Do data type conversions and create channels
    timestamps = np.array(timestamps, dtype="datetime64[ms]")
    channelInstances = []
    channelMap = {
        c.longName: c
        for _, c in inspect.getmembers(pychannels, predicate=lambda t: isinstance(t, Channel))
    }  # Maps longNames (keys) to channel datatypes (values) so we can get shortNames and _dbName
    dtype = [("timestamp", "datetime64[ms]")]
    for i, channelName in enumerate(channels):
        channelInstances.append(
            Channel(
                channelID=i,
                shortName=channelMap[channelName].shortName
                if channelName in channelMap
                else "cnt_00",
                longName=channelName,
                units=units[i],  # type: ignore
                unitsPlainText=units[i],  # type: ignore
                _dbName=channelMap[channelName]._dbName
                if channelName in channelMap
                else channelName,
            )
        )
        dtype.append((channelName, "float64"))

    # Populate as much of the RSK class instance as we can
    rsk.dbInfo = DbInfo(
        version=RSKEPDesktopReader.MAX_SUPPORTED_SEMVER,
        type=RSKEPDesktopReader.TYPE,
    )
    rsk.data = np.fromiter(
        ((timestamps[i], *v) for i, v in enumerate(values)),
        dtype=dtype,
        count=n,
    )
    rsk.channels = channelInstances
    rsk.instrument = Instrument(
        instrumentID=1,
        serialID=serialID,
        model=model,
    )
    rsk.deployment = Deployment(
        deploymentID=1,
        instrumentID=rsk.instrument.instrumentID,
        timeOfDownload=np.datetime64("now", "ms"),
        name=filename,
    )
    rsk.appSettings = [
        AppSetting(
            deploymentID=rsk.deployment.deploymentID,
            ruskinVersion=pyversion,
        )
    ]
    rsk.epoch = Epoch(
        deploymentID=rsk.deployment.deploymentID,
        startTime=rsk.data["timestamp"][0],
        endTime=rsk.data["timestamp"][1] if rsk.data.size > 1 else rsk.data["timestamp"][0],
    )
    # Chooses schedule type as "continuous" by default.
    # TODO: double-check whether if the above choice is reasonable
    rsk.schedule = Schedule(
        scheduleID=1,
        instrumentID=rsk.instrument.instrumentID,
        mode="continuous",
    )
    rsk.scheduleInfo = ContinuousInfo(
        continuousID=1,
        scheduleID=rsk.schedule.scheduleID,
        samplingPeriod=np.average(np.diff(rsk.data["timestamp"].astype("uint64"))),
    )

    rsk.appendlog("RSK instance created by the RSK.create() class method.")
    return rsk


def addchannel(
    self: RSK,
    data: Collection[float],
    channel: str = "unknown",
    units: str = "unknown",
    isMeasured: int = 0,
    isDerived: int = 0,
) -> None:
    """Add a new channel with a defined channel name and unit. If the new channel already
    exists in the current RSK instance, it will overwrite the old one.

    Args:
        data (npt.NDArray): Array containing the data to be added.
        channel (str, optional): name of the added channel. Defaults to "unknown".
        unit (str, optional): unit of the added channel. Defaults to "unknown".
        isMeasured (int, optional): whether the added channel is directly measured. Defaults to "0", not measured.
        isDerived (int,optional): whether the added channel is derived from other channels. Defaults to "0", not derived.

    Adds a new channel with a defined channel name and unit. If the new channel already exists in the :class:`RSK` structure,
    it will overwrite the old one.

    The data for the new channel must be stored in a field of newChan called "values" (i.e., ``newChan.values``).
    If the data is arranged as profiles in the current :class:`RSK` instance, then newChan must be a 1xN array of
    structures where N = len(:obj:`RSK.data`).

    Example:

    >>> # In this example we compute Absolute Salinity and add it to an :class:`RSK` instance
    ... # using the TEOS-10 GSW function "SA_from_SP".
    ... data = gsw.SA_from_SP(rsk.data["salinity"], rsk.data["sea_pressure"], -150, 49)
    ... rsk.addchannel(data, "absolute_salinity", units="g/kg", isMeasured = 0, isDerived = 1)
    """
    self.dataexistsorerror()

    if len(data) != len(self.data):
        raise ValueError(
            f"Expected len of argument 'data' to be {len(self.data)} but got len of {len(data)}."
        )

    formattedChannel = formatchannelname(channel)
    if channel != formattedChannel:
        self.printwarning(
            f"Argument 'channel' improperly formatted, did you mean {formattedChannel}?"
        )

    channelMap = {
        c.longName: c
        for _, c in inspect.getmembers(pychannels, predicate=lambda t: isinstance(t, Channel))
    }  # Maps longNames (keys) to channel datatypes (values) so we can get shortNames and _dbName

    if channel in channelMap:
        channelInstance = Channel(
            shortName=channelMap[channel].shortName,
            longName=channel,
            units=units,
            unitsPlainText=units,
            _dbName=channelMap[channel]._dbName,
        )
    else:
        channelInstance = Channel(
            longName=channel,
            shortName="cnt_00",
            units=units,
            unitsPlainText=units,
            _dbName=channel,
        )

    self.appendchannel(channelInstance, data, isMeasured, isDerived)
    self.appendlog(f"{channel} ({units}) added to data table by RSK.addchannel().")


def removecasts(self: RSK, direction: str = "up") -> None:
    """Remove the data elements with either an increasing or decreasing pressure.

    Args:
        direction (str, optional): cast direction of either "up" or "down". Defaults to "up".

    Removes either downcasts or upcasts in the current :class:`RSK` instance.

    **NOTE**: When there are only downcasts in the current :class:`RSK` instance, the request to
    remove downcasts will not take effect. The same for upcasts.

    Example:

    >>> rsk.removecasts(direction="up")
    """
    self.dataexistsorerror()
    self.channelsexistorerror(pychannels.Pressure)

    if direction not in ("up", "down"):
        raise ValueError(f"Invalid direction: {direction}.")

    # The only time this should fail is when we lack profiles in the other direction
    try:
        profileIndices = self.getprofilesindices(direction=direction)
    except ValueError:
        self.printwarning(f"There are only {direction}casts in this RSK instance.")
        return

    if len(profileIndices) == 0:
        self.printwarning(
            f"There are no {direction}casts in this RSK instance. Try RSK.computeprofiles()."
        )
        return

    self.data = np.delete(self.data, np.concatenate(profileIndices))

    self.regions = [
        r
        for r in self.regions
        if not isinstance(r, RegionCast) or r.regionType.lower() != direction
    ]

    self.appendlog(f"{direction}casts removed.")


def appendlog(self: RSK, logentry: str) -> None:
    """Append the entry and current time to the log field.

    Args:
        logentry (str): comment that will be added to the log.

    Appends the entry and current time to the log field.
    It is frequently called by other RSK methods for record use so that the users will not
    lose track of what happened to the file or the data. This method can also be called by
    the user to record any customized behaviour.

    Example:

    >>> rsk.appendlog(logentry="New channel practical salinity is added.")
    """
    # Funny cludge below. If this method is invoked twice at the same instant,
    # the second invocation will produce the same timestamp and overwrite
    # the first invocation's log. We want to save datetime in ms to be consistent
    # with the rest of the code, so limit by 1 ms instead
    # of doing the sensible thing of using nanoseconds.
    time.sleep(1.0 / 1000.0)

    self.logs[np.datetime64(time.time_ns() // 1_000_000, "ms")] = logentry


def printchannels(self: RSK) -> None:
    """Display instrument information, channel names, and units in the current RSK instance.

    Example:

    >>> rsk.printchannels()

    Example output::

        Model: RBRconcerto³
        Serial ID: 60662
        Sampling period: 0.125 second
            index              channel                unit
            _____    ____________________________    _______

            0        'conductivity'                  'mS/cm'
            1        'temperature'                   '°C'
            2        'pressure'                      'dbar'
            3        'temperature1'                  '°C'
            4        'temperature2'                  '°C'
            5        'sea_pressure'                  'dbar'
            6        'salinity'                      'PSU'
    """
    print(f"Model:           {self.instrument.model}")
    print(f"Serial ID:       {self.instrument.serialID}")
    print(f"Sampling period: {self.scheduleInfo.samplingperiod()} second")
    print(f"Channels:        index{' '*17}name{' '*18}unit")
    print(f"                 {'_'*5:<{10}}{'_'*28:<{32}}{'_'*8}")

    channelNames, channelUnits = self.getchannelnamesandunits([])
    for i in range(len(channelNames)):
        print(f"                 {i:<{10}}{channelNames[i]:<{32}}{channelUnits[i]}")


def getregionsbytypes(
    self: RSK, types: Union[Type[Region], Collection[Type[Region]]]
) -> List[Region]:
    """Retrieve all the regions from :obj:`.RSK.regions` that match
    the list of Region types passed in as an argument.

    NOTE: a Region type is any class that inherits from :class:`.Region`.

    Args:
        types (Union[Type[Region], Collection[Type[Region]]]): a single or list of Region type(s)

    Returns:
        List[Region]: the filtered list of Region instances obtained from :obj:`.RSK.regions`.
    """
    types = set(types) if hasattr(types, "__iter__") else {types}  # type: ignore
    return [region for region in self.regions if type(region) in types]
