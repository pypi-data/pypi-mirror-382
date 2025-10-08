#!/usr/bin/env python3
from __future__ import annotations
from typing import *
from dataclasses import dataclass, asdict
import numpy as np
import numpy.typing as npt
from numpy import datetime64


@dataclass
class Image:
    """
    Attributes:
        x (npt.NDArray): X axis list.
        y (npt.NDArray): Y axis list.
        channelNames (List[str]): Channel names for the generated data.
        channelUnits (List[str]): Units associated with each channel.
        profiles (Union[int, Collection[int]]): Profile number(s) for data that are generated.
        direction (str): Direction for data that are generated ('up' or 'down').
        data (npt.NDArray): Data matrix with dimension in x, y and number of channels.
        reference (str): Reference channel name.
        reference_unit (str): Reference channel unit.
    """

    x: npt.NDArray
    y: npt.NDArray
    channelNames: List[str]
    channelUnits: List[int]
    profiles: Union[int, Collection[int]]
    direction: str
    data: npt.NDArray
    reference: str
    referenceUnit: str


@dataclass(frozen=True)
class DbInfo:
    """
    Attributes:
        version (str): Defaults to None.
        type (str): Defaults to None.
    """

    version: str = None
    type: str = None


@dataclass(frozen=True)
class Instrument:
    """
    Attributes:
        instrumentID (int): Defaults to None.
        serialID (int): Defaults to None.
        model (str): Defaults to None.
        firmwareVersion (str): Defaults to None.
        firmwareType (str): Defaults to None.
        partNumber (str): Defaults to None.
    """

    instrumentID: int = None
    serialID: int = None
    model: str = None
    firmwareVersion: str = None
    firmwareType: int = None
    partNumber: str = None


@dataclass(frozen=True)
class Deployment:
    """
    Attributes:
        deploymentID (int): Defaults to None.
        instrumentID (int): Defaults to None.
        comment (str): Defaults to None.
        loggerStatus (str): Defaults to None.
        loggerTimeDrift (str): Defaults to None.
        timeOfDownload (str): Defaults to None.
        name (str): Defaults to None.
        sampleSize (int): Defaults to None.
        dataStorage (int): Defaults to None.
        loggerInitialStatus (int): Defaults to None.
    """

    deploymentID: int = None
    instrumentID: int = None
    comment: str = None
    loggerStatus: str = None
    loggerTimeDrift: int = None
    timeOfDownload: datetime64 = None
    name: str = None
    sampleSize: int = None
    dataStorage: int = None
    loggerInitialStatus: int = None


@dataclass(frozen=True)
class DiagnosticsChannels:
    """
    Attributes:
        id (int): Defaults to None.
        name (str): Defaults to None.
        unit (str): Defaults to None.
    """

    id: int = None
    name: str = None
    unit: str = None


@dataclass(frozen=True)
class DiagnosticsData:
    """
    Attributes:
        tstamp (datetime64): Defaults to None.
        channelid (str): Defaults to None.
        value (float): Defaults to None.
        instrumentID (int): Default to None.
        deviceIndex (int): Default to None.
    """

    tstamp: datetime64 = None
    channelid: str = None
    value: float = None
    instrumentID: int = None
    deviceIndex: int = None


@dataclass(frozen=True)
class GeoData:
    """
    Attributes:
        tstamp (datetime64): Defaults to None.
        latitude (float): Defaults to None.
        longitude (float): Defaults to None.
        accuracy (float): Defaults to None.
        accuracyType (str): Defaults to None.
    """

    tstamp: datetime64 = None
    latitude: float = None
    longitude: float = None
    accuracy: float = None
    accuracyType: str = None


@dataclass(frozen=True)
class Channel:
    """
    Attributes:
        channelID (int): Defaults to None.
        shortName (str): Defaults to None.
        longName (str): Defaults to None.
        unitsPlainText (str): Defaults to None.
        isMeasured (int): Defaults to None.
        isDerived (int): Defaults to None.
        units (str): Defaults to None.
        label (str): Defaults to "".
        feModuleType (str): Defaults to "".
        feModuleVersion (int): Defaults to 0.
    """

    channelID: int = None
    shortName: str = None
    longName: str = None
    unitsPlainText: str = None
    isMeasured: int = None
    isDerived: int = None
    units: str = None
    label: str = ""
    feModuleType: str = ""
    feModuleVersion: int = 0
    # Private undocumented variable to cache the name that would need to be stored back into the DB
    _dbName: str = None

    def withnewname(self, longName: str) -> Channel:
        tmp = asdict(self)
        tmp["longName"] = longName
        return Channel(**tmp)

    def withnewparams(
        self,
        channelID: int,
        isMeasured: int,
        isDerived: int,
    ) -> Channel:
        tmp = asdict(self)
        tmp["channelID"] = channelID
        tmp["isMeasured"] = isMeasured
        tmp["isDerived"] = isDerived

        return Channel(**tmp)


@dataclass(frozen=True)
class Epoch:
    """
    Attributes:
        deploymentID (int): Defaults to None.
        startTime (datetime64): Defaults to None.
        endTime (datetime64): Defaults to None.
    """

    deploymentID: int = None
    startTime: datetime64 = None
    endTime: datetime64 = None


@dataclass(frozen=True)
class Schedule:
    """
    Attributes:
        scheduleID (int): Defaults to None.
        instrumentID (int): Defaults to None.
        mode (str): Defaults to None.
        gate (str): Defaults to None.
    """

    scheduleID: int = None
    instrumentID: int = None
    mode: str = None
    gate: str = None


@dataclass(frozen=True)
class ScheduleInfo:
    """
    Attributes:
        scheduleID (int): Defaults to None.
    """

    scheduleID: int = None

    def samplingperiod(self) -> float:
        """Returns the sampling period in seconds."""
        raise NotImplementedError("Child class must implement this.")


@dataclass(frozen=True)
class WaveInfo(ScheduleInfo):
    """Inherits all the fields of :class:`ScheduleInfo`.

    Attributes:
        waveID (int): Defaults to None.
        samplingPeriod (int): Defaults to None.
        repetitionPeriod (int): Defaults to None.
        samplingCount (int): Defaults to None.
    """

    waveID: int = None
    samplingPeriod: int = None
    repetitionPeriod: int = None
    samplingCount: int = None

    def samplingperiod(self) -> float:
        return self.samplingPeriod / 1000.0


@dataclass(frozen=True)
class ContinuousInfo(ScheduleInfo):
    """Inherits all the fields of :class:`ScheduleInfo`.

    Attributes:
        continuousID (int): Defaults to None.
        samplingPeriod (int): Defaults to None.
    """

    continuousID: int = None
    samplingPeriod: int = None

    def samplingperiod(self) -> float:
        return self.samplingPeriod / 1000.0


@dataclass(frozen=True)
class BurstInfo(ScheduleInfo):
    """Inherits all the fields of :class:`ScheduleInfo`.

    Attributes:
        burstID (int): Defaults to None.
        samplingPeriod (int): Defaults to None.
        repetitionPeriod (int): Defaults to None.
        samplingCount (int): Defaults to None
    """

    burstID: int = None
    samplingPeriod: int = None
    repetitionPeriod: int = None
    samplingCount: int = None

    def samplingperiod(self) -> float:
        return self.samplingPeriod / 1000.0


@dataclass(frozen=True)
class TideInfo(ScheduleInfo):
    """Inherits all the fields of :class:`ScheduleInfo`.

    Attributes:
        tideID (int): Defaults to None.
        samplingPeriod (int): Defaults to None.
        repetitionPeriod (int): Defaults to None.
        samplingCount (int): Defaults to None
    """

    tideID: int = None
    samplingPeriod: int = None
    repetitionPeriod: int = None
    samplingCount: int = None

    def samplingperiod(self) -> float:
        return self.samplingPeriod / 1000.0


@dataclass(frozen=True)
class AverageInfo(ScheduleInfo):
    """Inherits all the fields of :class:`ScheduleInfo`.

    Attributes:
        averageID (int): Defaults to None.
        samplingPeriod (int): Defaults to None.
        repetitionPeriod (int): Defaults to None.
        samplingCount (int): Defaults to None
    """

    averageID: int = None
    samplingPeriod: int = None
    repetitionPeriod: int = None
    samplingCount: int = None

    def samplingperiod(self) -> float:
        return self.samplingPeriod / 1000.0


@dataclass(frozen=True)
class DirectionalInfo(ScheduleInfo):
    """Inherits all the fields of :class:`ScheduleInfo`.

    Attributes:
        directionalID (int): Defaults to None.
        direction (str): Defaults to None.
        fastPeriod (int): Defaults to None.
        slowPeriod (int): Defaults to None.
        fastThreshold (float): Defaults to None.
        slowThreshold (float): Defaults to None.
    """

    directionalID: int = None
    direction: str = None
    fastPeriod: int = None
    slowPeriod: int = None
    fastThreshold: float = None
    slowThreshold: float = None

    def samplingperiod(self) -> float:
        return self.fastPeriod / 1000.0

    def samplingperiodslow(self) -> float:
        return self.slowPeriod / 1000.0


@dataclass(frozen=True)
class Power:
    """
    Attributes:
        deploymentID (int): Defaults to None.
        internalBatteryType (int): Defaults to 0.
        externalBatteryType (int): Defaults to 100.
        internalBatteryCapacity (float): Defaults to 0.0.
        externalBatteryCapacity (float): Defaults to 0.0.
        internalEnergyUsed (float): Defaults to 0.0.
        externalEnergyUsed (float): Defaults to 0.0.
        e1 (float): Defaults to 0.0.
        p1 (float): Defaults to 0.0.
        p2 (float): Defaults to 0.0.
        p3 (float): Defaults to 0.0.
        powerSupplyPartNumber (str): Defaults to "".
        cellCount (int): Defaults to 0.
    """

    deploymentID: int = None
    internalBatteryType: int = 0
    externalBatteryType: int = 100
    internalBatteryCapacity: float = 0.0
    externalBatteryCapacity: float = 0.0
    internalEnergyUsed: float = 0.0
    externalEnergyUsed: float = 0.0
    e1: float = 0.0
    p1: float = 0.0
    p2: float = 0.0
    p3: float = 0.0
    powerSupplyPartNumber: str = ""
    cellCount: int = 0


@dataclass(frozen=True)
class Calibration:
    """
    The c, x, and n attributes are dictionaries where each key maps
    the calibration coefficient number, e.g., 0, 2, 10, etc, to
    its respective coefficient value.

    Taking the c attributes as an example, suppose we had calibration
    data with the ``c0``, ``c1``, and ``c3`` coefficients with values
    ``10.0``, ``NULL``, ``50.0``; then :obj:`.Calibration.c` would look like:

    .. code-block::

        {
            0: 10.0,
            1: nan,
            3: 50.0,
        }

    Attributes:
        calibrationID (int): Defaults to None.
        channelOrder (int): Defaults to None.
        instrumentID (int): Defaults to None
        type (str): Defaults to None.
        tstamp (datetime64): Defaults to None.
        equation (str): Defaults to None.
        c (Dict[int, np.floating]): Dictionary containing c coefficients. Defaults to None.
        x (Dict[int, np.floating]): Dictionary containing x coefficients. Defaults to None.
        n (Dict[int, np.integer]): Dictionary containing n coefficients. Defaults to None.
    """

    calibrationID: int = None
    channelOrder: int = None
    instrumentID: int = None
    type: str = None
    tstamp: datetime64 = None
    equation: str = None
    c: Dict[int, np.floating] = None
    x: Dict[int, np.floating] = None
    n: Dict[int, np.integer] = None


@dataclass(frozen=True)
class Parameter:
    """
    Attributes:
        parameterID (int): Defaults to None.
        tstamp (datetime64): Defaults to None.
    """

    parameterID: int = None
    tstamp: datetime64 = None


@dataclass(frozen=True)
class ParameterKey:
    """
    Attributes:
        parameterID (int): Defaults to None.
        key (str): Defaults to None.
        value (str): Defaults to None.
    """

    parameterID: int = None
    key: str = None
    value: str = None


@dataclass(frozen=True)
class AppSetting:
    """
    Attributes:
        deploymentID (int): Defaults to None.
        ruskinVersion (str): Defaults to None.
    """

    deploymentID: int = None
    ruskinVersion: str = None


@dataclass(frozen=True)
class Range:
    """
    Attributes:
        instrumentID (int): Defaults to None.
        channelID (int): Defaults to None.
        channelOrder (int): Defaults to None.
        mode (str): Defaults to None.
        gain (float): Defaults to None.
        availableGains (str): Defaults to None.
    """

    instrumentID: int = None
    channelID: int = None
    channelOrder: int = None
    mode: str = None
    gain: float = None
    availableGains: str = None


@dataclass(frozen=True)
class InstrumentSensor:
    """
    Attributes:
        instrumentID (int): Defaults to None.
        sensorID (int): Defaults to None.
        channelOrder (int): Defaults to None.
        serialID (int): Defaults to None.
        details (str): Defaults to None.
    """

    instrumentID: int = None
    sensorID: int = None
    channelOrder: int = None
    serialID: int = None
    details: str = None


@dataclass(frozen=True)
class InstrumentChannel:
    """
    Attributes:
        instrumentID (int): Defaults to None.
        channelID (int): Defaults to None.
        channelOrder (int): Defaults to None.
        channelStatus (int): Defaults to None.
    """

    instrumentID: int = None
    channelID: int = None
    channelOrder: int = None
    channelStatus: int = None


@dataclass(frozen=True)
class Region:
    """
    Attributes:
        datasetID (int): Defaults to None.
        regionID (int): Defaults to None.
        type (str): Defaults to None.
        tstamp1 (datetime64): Defaults to None.
        tstamp2 (datetime64): Defaults to None.
        label (str): Defaults to None.
        description (str): Defaults to None.
        collapsed (bool): Defaults to False.
    """

    datasetID: int = None
    regionID: int = None
    type: str = None
    tstamp1: datetime64 = None
    tstamp2: datetime64 = None
    label: str = None
    description: str = None
    collapsed: bool = False

    def __str__(self: Region) -> str:
        return f"{self.type} [{self.tstamp1}, {self.tstamp2}]"

    def __eq__(self: Region, other: object) -> bool:
        if not isinstance(other, Region):
            return NotImplemented

        return bool(
            self.tstamp1 == other.tstamp1 and self.tstamp2 == other.tstamp2
        )  # and self.type == other.type)

    def __ne__(self: Region, other: object) -> bool:
        if not isinstance(other, Region):
            return NotImplemented

        return bool(self.tstamp1 != other.tstamp1 or self.tstamp2 != other.tstamp2)

    def __gt__(self: Region, other: object) -> bool:
        if not isinstance(other, Region):
            return NotImplemented

        return bool(
            (self.tstamp1 > other.tstamp1 and self.tstamp2 > other.tstamp2)
            or (self.tstamp1 <= other.tstamp1 and self.tstamp2 >= other.tstamp2)
            # or (self.tstamp1 == other.tstamp1 and self.tstamp2 == other.tstamp2 and self.type > other.type)
        )

    def __lt__(self: Region, other: object) -> bool:
        if not isinstance(other, Region):
            return NotImplemented

        return bool(
            (self.tstamp1 < other.tstamp1 and self.tstamp2 < other.tstamp2)
            or (self.tstamp1 >= other.tstamp1 and self.tstamp2 <= other.tstamp2)
            # or (self.tstamp1 == other.tstamp1 and self.tstamp2 == other.tstamp2 and self.type < other.type)
        )


@dataclass(frozen=True)
class RegionCast(Region):
    """Inherits all the fields of :class:`Region`.

    Attributes:
        regionProfileID (int): Defaults to None.
        regionType (str): Defaults to None.
    """

    regionProfileID: int = None
    regionType: str = None

    def __str__(self: RegionCast) -> str:
        return f"{self.regionType}{self.type} [{self.tstamp1}, {self.tstamp2}]"

    def isdowncast(self: RegionCast) -> bool:
        return True if self.regionType == "DOWN" else False

    def isupcast(self: RegionCast) -> bool:
        return True if self.regionType == "UP" else False


@dataclass(frozen=True)
class RegionProfile(Region):
    """Inherits all the fields of :class:`Region`."""

    pass


@dataclass(frozen=True)
class RegionCal(Region):
    """Inherits all the fields of :class:`Region`.

    Attributes:
        plateauSize (int): Defaults to None.
        channelID (int): Defaults to None.
        sourceID (int): Defaults to None.
    """

    plateauSize: int = None
    channelID: int = None
    sourceID: int = None


@dataclass(frozen=True)
class RegionComment(Region):
    """Inherits all the fields of :class:`Region`.

    Attributes:
        content (str): Defaults to None.
    """

    content: str = None


@dataclass(frozen=True)
class RegionExclude(Region):
    """Inherits all the fields of :class:`Region`.

    Attributes:
        enable (bool): Defaults to None.
        regionType (str): Defaults to None.
    """

    enable: bool = None
    regionType: str = None


@dataclass(frozen=True)
class RegionGeoData(Region):
    """Inherits all the fields of :class:`Region`.

    Attributes:
        latitude (float): Defaults to None.
        longitude (float): Defaults to None.
    """

    latitude: float = None
    longitude: float = None


@dataclass(frozen=True)
class RegionPlateau(Region):
    """Inherits all the fields of :class:`Region`.

    Attributes:
        regionCalID (int): Defaults to 0.
        refValue (float): Defaults to None.
        refUnit (str): Defaults to None.
    """

    regionCalID: int = 0
    refValue: float = None
    refUnit: str = None


@dataclass(frozen=True)
class RegionAtmosphere(Region):
    """Inherits all the fields of :class:`Region`.

    Attributes:
        pressure (float): Defaults to None.
        unit (str): Defaults to None.
    """

    pressure: float = None
    unit: str = None
