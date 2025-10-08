#!/usr/bin/env python3
# Standard/external imports
from __future__ import annotations
from typing import *
import numpy as np
from pathlib import Path
import os
from datetime import datetime
import sqlite3

# Module imports
from pyrsktools.channels import *
from pyrsktools.datatypes import *
from pyrsktools.utils import datetime2rsktime

if TYPE_CHECKING:
    from typing import TextIO
    from pyrsktools import RSK


def RSK2CSV(
    self: RSK,
    channels: Union[str, Collection[str]] = [],
    profiles: Optional[Union[int, Collection[int]]] = None,
    direction: str = "both",
    outputDir: str = ".",
    comment: Optional[str] = None,
) -> None:
    """Write one or more CSV files of logger data and metadata.

    Args:
        channels (Union[str, Collection[str]], optional): longName of channel(s) for output files,
            if no value is given it will output all channels. Defaults to [] (all available channels).
        profiles (Union[int, Collection[int]], optional): profile number(s) for output files. If not specified, data will
            not be exported in profiles. Specify [] for all profiles. Defaults to None.
        direction (str, optional): cast direction of either "up", "down", or "both" for output files. Defaults to "both".
        outputDir (str, optional): directory for output files. Defaults to "." (current working directory).
        comment (str, optional): extra comments to attach to the end of the header. Defaults to None.

    Outputs channel data and metadata from the :class:`RSK` into one or more CSV files.
    The CSV file header contains logger metadata. The data table starts with a row of variable names and units above each column of channel data.
    If the ``profiles`` number is specified as an argument, then one file will be written for each profile. Furthermore, an extra column called "cast_direction" will be included.
    The column will contain 'd' or 'u' to indicate whether the sample is part of the downcast or upcast, respectively.

    Users can customize which channel, profile for outputs, output directory and comments are attached to the end of the header.

    Example:

    >>> with RSK("example.rsk") as rsk:
    ...     rsk.computeprofiles()
    ...     rsk.RSK2CSV(channels=["conductivity","pressure","dissolved_o2_concentration"], profiles = range(0,3), outputDir="/users/decide/where", comment="My data")

    Example of a CSV file created by this method::

        // Creator: RBR Ltd.
        // Create time: 2022-05-20T19:54:26
        // Instrument model firmware and serialID: RBRmaestro 12.03 80217
        // Sample period: 0.167 second
        // Processing history:
        //     /rsk_files/080217_20220919_1417.rsk opened using RSKtools v1.0.0.
        //     Sea pressure calculated using an atmospheric pressure of 10.1325 dbar.
        // Comment: My data

        // timestamp(yyyy-mm-ddTHH:MM:ss.FFF),  conductivity(mS/cm),   pressure(dbar),   dissolved_o2_concentration(%)
        2015-09-19T08:32:16.000,                 34.6058,           12.6400,          694.7396
        2015-09-19T08:32:16.167,                 34.6085,           12.4154,          682.4502
        2015-09-19T08:32:16.333,                 34.6130,           12.4157,          666.1949
    """
    # Check if the output dir exists
    if not os.path.isdir(outputDir):
        raise OSError(f"Output directory '{outputDir}' does not exist.")

    self.dataexistsorerror()
    self.channelsexistorerror(channels)

    channelNames, channelUnits = self.getchannelnamesandunits(channels)
    currentDate = str(np.datetime64("now"))
    spacing = " " * 4  # Spacing between data columns

    def _createCSVWithMetadata(filename: str) -> TextIO:
        fd = open(filename, "w")

        fd.write("// Creator: RBR Ltd.\n")
        fd.write(f"// Create time: {currentDate}\n")
        fd.write(
            "// Instrument model firmware and serialID: {} {} {}\n".format(
                self.instrument.model,
                self.instrument.firmwareVersion,
                self.instrument.serialID,
            )
        )
        fd.write(f"// Sample period: {self.scheduleInfo.samplingperiod()} second\n")
        fd.write(f"// Processing history:\n")
        for info in self.logs.values():
            fd.write(f"//\t{info}\n")
        if comment is not None:
            fd.write(f"// Comment: {comment}\n")

        columnNames = f"\n// timestamp(yyyy-mm-ddTHH:MM:ss.FFF),{spacing}"
        columnNames += f",{spacing}".join(
            f"{channelNames[i]}({channelUnits[i]})" for i in range(len(channelNames))
        )

        if profiles is not None:
            columnNames += f",{spacing}cast_direction"
        columnNames += "\n"

        fd.write(columnNames)

        return fd

    if profiles is not None:
        # A list of dicts, where each dict has keys for "d", "u", both "d" and "u",
        # with values being the profiles associated with each direction.
        # The length of this array is the number of profiles.
        profileIndicesDictList = []
        if direction not in {"up", "down", "both"}:
            raise ValueError(f"Invalid cast direction: {direction}")

        if direction == "both":
            upIndices = self.getprofilesindices(profiles, "up")
            downIndices = self.getprofilesindices(profiles, "down")
            assert len(upIndices) == len(downIndices)

            profileIndicesDictList = [
                {"d": downIndices[i], "u": upIndices[i]} for i in range(len(upIndices))
            ]
        else:
            castDirection = "u" if direction == "up" else "d"
            profileIndicesDictList = [
                {castDirection: indices} for indices in self.getprofilesindices(profiles, direction)
            ]

        # Too complicated!
        for i, profilesDict in enumerate(profileIndicesDictList):
            outputFilename = Path(self.filename).stem + f"_profile{i}" ".csv"
            fd = _createCSVWithMetadata(f"{outputDir}/{outputFilename}")

            for direction, indices in profilesDict.items():
                for row in self.data[["timestamp"] + channelNames][indices]:
                    fd.write(
                        f",{spacing}".join(str(c) for c in row) + f",{spacing}{direction}" + "\n"
                    )

            fd.close()
            print(f"Wrote: {outputDir}/{outputFilename}")
    else:
        outputFilename = Path(self.filename).stem + ".csv"
        fd = _createCSVWithMetadata(f"{outputDir}/{outputFilename}")

        for row in self.data[["timestamp"] + channelNames]:
            fd.write(f",{spacing}".join(str(c) for c in row) + "\n")

        fd.close()
        print(f"Wrote: {outputDir}/{outputFilename}")


def _createschema(db: sqlite3.Connection, tableMap: dict) -> None:
    cur = db.cursor()
    for tableName, tableInfo in tableMap.items():
        columns = ", ".join([f"{n} {t}" for n, t in tableInfo["columns"].items()])
        seperator = "," if len(tableInfo["constraints"]) > 0 else ""
        constraints = " ".join([c for c in tableInfo["constraints"]])
        query = f"CREATE TABLE {tableName} ({columns} {seperator} {constraints})"
        cur.execute(query)

    cur.close()


def _writedata(db: sqlite3.Connection, tableMap: dict, rsk: RSK) -> None:
    cur = db.cursor()
    columnValues: List[Any] = []

    if rsk.dbInfo:
        tableName = "dbInfo"
        columnNames = ", ".join(tableMap[tableName]["columns"].keys())
        columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
        columnValues = [
            rsk.dbInfo.version,
            rsk.dbInfo.type,
        ]
        cur.execute(f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})", columnValues)

    if rsk.instrument:
        tableName = "instruments"
        columnNames = ", ".join(tableMap[tableName]["columns"].keys())
        columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
        columnValues = [
            rsk.instrument.instrumentID,
            rsk.instrument.serialID,
            rsk.instrument.model,
            rsk.instrument.firmwareVersion,
            rsk.instrument.firmwareType,
            rsk.instrument.partNumber,
        ]
        cur.execute(f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})", columnValues)

    if rsk.deployment:
        tableName = "deployments"
        columnNames = ", ".join(tableMap[tableName]["columns"].keys())
        columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
        columnValues = [
            rsk.deployment.deploymentID,
            rsk.deployment.instrumentID,
            rsk.deployment.comment,
            rsk.deployment.loggerStatus,
            rsk.deployment.loggerTimeDrift,
            datetime2rsktime(rsk.deployment.timeOfDownload),
            rsk.deployment.name,
            rsk.deployment.sampleSize,
            rsk.deployment.dataStorage,
            rsk.deployment.loggerInitialStatus,
        ]
        cur.execute(f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})", columnValues)

    if rsk.channels:
        tableName = "channels"
        columnNames = ", ".join(tableMap[tableName]["columns"].keys())
        columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
        for channel in rsk.channels:
            columnValues = [
                channel.channelID,
                channel.shortName,
                channel._dbName,
                channel.units,
                channel._dbName,
                channel.unitsPlainText,
                channel.isMeasured,
                channel.isDerived,
                channel.label,
                channel.feModuleType,
                channel.feModuleVersion,
            ]
            cur.execute(
                f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})",
                columnValues,
            )

    if rsk.epoch:
        tableName = "epochs"
        columnNames = ", ".join(tableMap[tableName]["columns"].keys())
        columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
        columnValues = [
            rsk.epoch.deploymentID,
            datetime2rsktime(rsk.epoch.startTime),
            datetime2rsktime(rsk.epoch.endTime),
        ]
        cur.execute(f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})", columnValues)

    if rsk.schedule:
        tableName = "schedules"
        columnNames = ", ".join(tableMap[tableName]["columns"].keys())
        columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
        columnValues = [
            rsk.schedule.scheduleID,
            rsk.schedule.instrumentID,
            rsk.schedule.mode,
            rsk.schedule.gate,
        ]
        cur.execute(f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})", columnValues)

    if rsk.scheduleInfo:
        if isinstance(rsk.scheduleInfo, WaveInfo):
            tableName = "wave"
            columnNames = ", ".join(tableMap[tableName]["columns"].keys())
            columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
            columnValues = [
                rsk.scheduleInfo.waveID,
                rsk.scheduleInfo.scheduleID,
                rsk.scheduleInfo.samplingperiod(),
                rsk.scheduleInfo.repetitionPeriod,
                rsk.scheduleInfo.samplingCount,
            ]
            cur.execute(
                f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})", columnValues
            )
        elif isinstance(rsk.scheduleInfo, ContinuousInfo):
            tableName = "continuous"
            columnNames = ", ".join(tableMap[tableName]["columns"].keys())
            columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
            columnValues = [
                rsk.scheduleInfo.continuousID,
                rsk.scheduleInfo.scheduleID,
                rsk.scheduleInfo.samplingPeriod,
            ]
            cur.execute(
                f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})", columnValues
            )
        elif isinstance(rsk.scheduleInfo, BurstInfo):
            tableName = "burst"
            columnNames = ", ".join(tableMap[tableName]["columns"].keys())
            columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
            columnValues = [
                rsk.scheduleInfo.burstID,
                rsk.scheduleInfo.scheduleID,
                rsk.scheduleInfo.samplingPeriod,
                rsk.scheduleInfo.repetitionPeriod,
                rsk.scheduleInfo.samplingCount,
            ]
            cur.execute(
                f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})", columnValues
            )
        elif isinstance(rsk.scheduleInfo, TideInfo):
            tableName = "tide"
            columnNames = ", ".join(tableMap[tableName]["columns"].keys())
            columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
            columnValues = [
                rsk.scheduleInfo.tideID,
                rsk.scheduleInfo.scheduleID,
                rsk.scheduleInfo.samplingPeriod,
                rsk.scheduleInfo.repetitionPeriod,
                rsk.scheduleInfo.samplingCount,
            ]
            cur.execute(
                f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})", columnValues
            )
        elif isinstance(rsk.scheduleInfo, AverageInfo):
            tableName = "average"
            columnNames = ", ".join(tableMap[tableName]["columns"].keys())
            columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
            columnValues = [
                rsk.scheduleInfo.averageID,
                rsk.scheduleInfo.scheduleID,
                rsk.scheduleInfo.samplingPeriod,
                rsk.scheduleInfo.repetitionPeriod,
                rsk.scheduleInfo.samplingCount,
            ]
            cur.execute(
                f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})", columnValues
            )
        elif isinstance(rsk.scheduleInfo, DirectionalInfo):
            tableName = "directional"
            columnNames = ", ".join(tableMap[tableName]["columns"].keys())
            columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
            columnValues = [
                rsk.scheduleInfo.directionalID,
                rsk.scheduleInfo.scheduleID,
                rsk.scheduleInfo.direction,
                rsk.scheduleInfo.fastPeriod,
                rsk.scheduleInfo.slowPeriod,
                rsk.scheduleInfo.fastThreshold,
                rsk.scheduleInfo.slowThreshold,
            ]
            cur.execute(
                f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})", columnValues
            )

    if rsk.regions:
        for region in rsk.regions:
            tableName = "region"
            columnNames = ", ".join(tableMap[tableName]["columns"].keys())
            columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
            columnValues = [
                region.datasetID,
                region.regionID,
                region.type,
                datetime2rsktime(region.tstamp1),
                datetime2rsktime(region.tstamp2),
                region.label,
                region.description,
                region.collapsed,
            ]
            cur.execute(
                f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})", columnValues
            )

            if isinstance(region, RegionCal):
                tableName = "regionCal"
                columnValues = [
                    region.regionID,
                    region.plateauSize,
                    region.channelID,
                    region.sourceID,
                ]
            elif isinstance(region, RegionCast):
                tableName = "regionCast"
                columnValues = [
                    region.regionID,
                    region.regionProfileID,
                    region.regionType,
                ]
            elif isinstance(region, RegionComment):
                tableName = "regionComment"
                columnValues = [
                    region.regionID,
                    region.content,
                ]
            elif isinstance(region, RegionExclude):
                tableName = "regionExclude"
                columnValues = [
                    region.regionID,
                    region.enable,
                    region.regionType,
                ]
            elif isinstance(region, RegionGeoData):
                tableName = "regionGeoData"
                columnValues = [
                    region.regionID,
                    region.latitude,
                    region.longitude,
                ]
            elif isinstance(region, RegionPlateau):
                tableName = "regionPlateau"
                columnValues = [
                    region.regionID,
                    region.regionCalID,
                    region.refValue,
                    region.refUnit,
                ]
            elif isinstance(region, RegionProfile):
                tableName = "regionProfile"
                columnValues = [
                    region.regionID,
                ]
            elif isinstance(region, RegionAtmosphere):
                tableName = "regionAtmosphere"
                columnValues = [
                    region.regionID,
                    region.pressure,
                    region.unit,
                ]

            columnNames = ", ".join(tableMap[tableName]["columns"].keys())
            columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
            cur.execute(
                f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})", columnValues
            )

    if rsk.schedule:
        tableName = "power"
        columnNames = ", ".join(tableMap[tableName]["columns"].keys())
        columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
        for power in rsk.power:
            columnValues = [
                power.deploymentID,
                power.internalBatteryType,
                power.externalBatteryType,
                power.internalBatteryCapacity,
                power.externalBatteryCapacity,
                power.internalEnergyUsed,
                power.externalEnergyUsed,
                power.e1,
                power.p1,
                power.p2,
                power.p3,
                power.powerSupplyPartNumber,
                power.cellCount,
            ]
            cur.execute(
                f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})", columnValues
            )

    if rsk.calibrations:
        calTableName = "calibrations"
        calColumnNames = ", ".join(tableMap[calTableName]["columns"].keys())
        calColumnBinds = ("?, " * (len(tableMap[calTableName]["columns"]))).rstrip(", ")

        coefTableName = "coefficients"
        coefColumnNames = ", ".join(tableMap[coefTableName]["columns"].keys())
        coefColumnBinds = ("?, " * (len(tableMap[coefTableName]["columns"]))).rstrip(", ")

        prevCalID = -1
        for calibration in rsk.calibrations:
            if prevCalID != calibration.calibrationID:
                columnValues = [
                    calibration.calibrationID,
                    calibration.channelOrder,
                    calibration.instrumentID,
                    calibration.type,
                    datetime2rsktime(calibration.tstamp),
                    calibration.equation,
                ]
                cur.execute(
                    f"INSERT INTO {calTableName} ({calColumnNames}) VALUES ({calColumnBinds})",
                    columnValues,
                )

            if calibration.c:
                for i, c in calibration.c.items():
                    columnValues = [
                        calibration.calibrationID,
                        f"c{i}",
                        c,
                    ]
                    cur.execute(
                        f"INSERT INTO {coefTableName} ({coefColumnNames}) VALUES ({coefColumnBinds})",
                        columnValues,
                    )

            if calibration.x:
                for i, x in calibration.x.items():
                    columnValues = [
                        calibration.calibrationID,
                        f"x{i}",
                        x,
                    ]
                    cur.execute(
                        f"INSERT INTO {coefTableName} ({coefColumnNames}) VALUES ({coefColumnBinds})",
                        columnValues,
                    )

            if calibration.n:
                for i, n in calibration.n.items():
                    columnValues = [
                        calibration.calibrationID,
                        f"n{i}",
                        n,
                    ]
                    cur.execute(
                        f"INSERT INTO {coefTableName} ({coefColumnNames}) VALUES ({coefColumnBinds})",
                        columnValues,
                    )
            prevCalID = calibration.calibrationID

    if rsk.parameters:
        tableName = "parameters"
        columnNames = ", ".join(tableMap[tableName]["columns"].keys())
        columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
        for parameter in rsk.parameters:
            columnValues = [
                parameter.parameterID,
                datetime2rsktime(parameter.tstamp),
            ]
            cur.execute(
                f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})", columnValues
            )

    if rsk.parameterKeys:
        tableName = "parameterKeys"
        columnNames = ", ".join(tableMap[tableName]["columns"].keys())
        columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
        for pKey in rsk.parameterKeys:
            columnValues = [
                pKey.parameterID,
                pKey.key,
                pKey.value,
            ]
            cur.execute(
                f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})", columnValues
            )

    if rsk.appSettings:
        tableName = "appSettings"
        columnNames = ", ".join(tableMap[tableName]["columns"].keys())
        columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
        for a in rsk.appSettings:
            columnValues = [
                a.deploymentID,
                a.ruskinVersion,
            ]
            cur.execute(
                f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})", columnValues
            )

    if rsk.ranging:
        tableName = "ranging"
        columnNames = ", ".join(tableMap[tableName]["columns"].keys())
        columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
        for r in rsk.ranging:
            columnValues = [
                r.instrumentID,
                r.channelID,
                r.channelOrder,
                r.mode,
                r.gain,
                r.availableGains,
            ]
            cur.execute(
                f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})", columnValues
            )

    if rsk.instrumentSensors:
        tableName = "instrumentSensors"
        columnNames = ", ".join(tableMap[tableName]["columns"].keys())
        columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
        for s in rsk.instrumentSensors:
            columnValues = [
                s.instrumentID,
                s.sensorID,
                s.channelOrder,
                s.serialID,
                s.details,
            ]
            cur.execute(
                f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})", columnValues
            )

    if rsk.instrumentChannels:
        tableName = "instrumentChannels"
        columnNames = ", ".join(tableMap[tableName]["columns"].keys())
        columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
        for iC in rsk.instrumentChannels:
            columnValues = [
                iC.instrumentID,
                iC.channelID,
                iC.channelOrder,
                iC.channelStatus,
            ]
            cur.execute(
                f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})", columnValues
            )

    if rsk.data.size > 0:
        tableName = "data"
        columnNames = ", ".join(tableMap[tableName]["columns"].keys())
        columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
        query = f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})"

        cur.executemany(
            query,
            ((datetime2rsktime(data["timestamp"]), *data[rsk.channelNames]) for data in rsk.data),
        )

    if rsk.processedData.size > 0:
        tableName = "burstData"
        columnNames = ", ".join(tableMap[tableName]["columns"].keys())
        columnBinds = ("?, " * (len(tableMap[tableName]["columns"]))).rstrip(", ")
        query = f"INSERT INTO {tableName} ({columnNames}) VALUES ({columnBinds})"

        cur.executemany(
            query,
            (
                (datetime2rsktime(data["timestamp"]), *data[rsk.processedChannelNames])
                for data in rsk.processedData
            ),
        )

    cur.close()


def RSK2RSK(self: RSK, outputDir: str = ".", suffix: Optional[str] = None) -> str:
    """Write the current :class:`RSK` instance into a new RSK file.

    Args:
        outputDir (str, optional): directory for output RSK file. Defaults to "." (current working directory).
        suffix (str, optional): string to append to output rsk file name. Defaults to None (current time in the format of YYYYMMDDTHHMM).

    Returns:
        str: file name of output RSK file.

    Writes a new RSK file containing the data and various metadata from the current :class:`RSK` instance.
    It is designed to store post-processed data in a SQLite file that is readable by Ruskin.
    The new rsk file is in "EPdesktop" format, which is the simplest Ruskin table schema.
    This method effectively provides a convenient method for Python users to easily share post-processed RBR logger
    data with others without recourse to CSV, MAT, or ODV files.

    The tables created by this method include:

    * channels
    * data
    * dbinfo
    * deployments
    * downloads
    * epochs
    * errors
    * events
    * instruments
    * region
    * regionCast
    * regionComment
    * regionGeoData
    * regionProfile
    * schedules

    Example:

    >>> with RSK("example.rsk") as rsk:
    ...     rsk.readdata()
    ...     rsk.computeprofiles()
    ...     outputfilename = rsk.RSK2RSK(outputDir="/users/decide/where", suffix="processed")
    """
    from pyrsktools._rsk._table_map import create_rsk_table_map

    outputDir: Path = Path(outputDir)
    # Get the name of the currently opened RSK (without the .rsk suffix)
    name = Path(self.filename).stem
    # If user did not give us a suffix, make it the current date
    if not suffix:
        suffix = datetime.now().strftime("%Y%m%dT%H%M")
    # Output file name is the current file name plus the suffixes
    outputFileName: Path = Path(f"{name}_{suffix}.rsk")
    outputFilePath: Path = outputDir / outputFileName

    if outputFilePath.is_file():
        raise FileExistsError(
            f"{outputFilePath} already exists, please revise suffix for a different name."
        )

    tableMap = create_rsk_table_map(self)
    with sqlite3.connect(outputFilePath) as db:
        _createschema(db, tableMap)
        _writedata(db, tableMap, self)

    return outputFilePath.name
