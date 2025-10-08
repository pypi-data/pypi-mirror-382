#!/usr/bin/env python3
# Standard/external imports
from __future__ import annotations
from typing import *
import sqlite3
import re
from enum import IntEnum
import dataclasses
import numpy as np
import numpy.typing as npt
from abc import ABC, abstractmethod

# Module imports
from pyrsktools.datatypes import *
from pyrsktools.utils import semver2int, datetime2rsktime, rsktime2datetime, formatchannelname


class ChannelStatus(IntEnum):
    CONCEALED = 0x1  # 1 = hidden, 0 = visible
    IGNORED = 0x2  # 1 = not sampled, 0 = sampled
    TRANSIENT = 0x04  # 1 = not stored, 0 = stored
    QUIET = 0x08  # 1 = not streamed, 0 = streamed
    USEROFF = 0x10  # 1 = user disabled, 0 = enabled


class Reader(ABC):
    """Reader base class.

    NOTE: for reading RSK files only!

    NOTE: the default methods for querying data from RSKs provided by this class
    are extremely reliant on the definition of pyrsktools.attributes. Further,
    these methods assume the RSK file is of type "EPDesktop" version 2.16.0.

    These defaults SHOULD NOT be relied upon. Instead, reader classes inheriting
    from this should override each and every method that has known differences
    between EPDesktop 2.16.0. The method overrides should handle all versioning
    complexity and populate the appropriate classes from pyrsktools.attributes.
    """

    TYPE: Optional[str] = None
    MIN_SUPPORTED_SEMVER: str = None
    MAX_SUPPORTED_SEMVER: str = None
    # Region type mapping maps the datatype to a tablename
    # and the 'type' name found in the 'region' table of an RSK.
    # NOTE: if these change for a given RSK type or version of said RSK type,
    # the RSK reader inheriting from this class can/must edit this class variable
    # in its __init__ method.
    REGION_TYPE_MAPPING: dict = {
        RegionCal: {"table": "regionCal", "type": "CALIBRATION"},
        RegionCast: {"table": "regionCast", "type": "CAST"},
        RegionComment: {"table": "regionComment", "type": "COMMENT"},
        RegionExclude: {"table": "regionExclude", "type": "EXCLUSION"},
        RegionGeoData: {"table": "regionGeoData", "type": "GPS"},
        RegionPlateau: {"table": "regionPlateau", "type": "PLATEAU"},
        RegionProfile: {"table": "regionProfile", "type": "PROFILE"},
        RegionAtmosphere: {"table": "regionAtmosphere", "type": "ATMOSPHERE"},
    }

    def __init__(self: Reader, db: sqlite3.Connection, semver: str) -> None:
        if not self.TYPE or not self.MIN_SUPPORTED_SEMVER or not self.MAX_SUPPORTED_SEMVER:
            raise TypeError("Direct instantiation of the Reader class is prohibited.")

        self.version: int = semver2int(semver)

        # If current RSK version is not supported and it is has a version lesser than the latest version
        # we support, raise error.
        if self.version < semver2int(self.MIN_SUPPORTED_SEMVER) or self.version > semver2int(
            self.MAX_SUPPORTED_SEMVER
        ):
            raise ValueError(
                f"Loaded '{self.TYPE}' RSK version is unsupported: {semver}. "
                f"Current support for: {self.MIN_SUPPORTED_SEMVER} <= version <= {self.MAX_SUPPORTED_SEMVER}"
            )

        db.row_factory = sqlite3.Row
        self._db: sqlite3.Connection = db
        self._tables: Set[str] = self._getTables()

    def _getTables(self: Reader) -> Set[str]:
        cur = self._db.cursor()
        cur.execute(f"SELECT name FROM sqlite_master WHERE type = 'table'")

        return {row[0] for row in cur.fetchall()}

    def _getTableColumns(self: Reader, table: str) -> List[str]:
        cur = self._db.cursor()
        cur.execute(f"PRAGMA table_info({table})")

        return [row[1] for row in cur.fetchall()]

    def _query(
        self: Reader,
        table: str,
        columns: Optional[Collection[str]] = None,
        where: Optional[str] = None,
        orderByAsc: Optional[str] = None,
        orderByDesc: Optional[str] = None,
        limit: Optional[int] = None,
        innerJoin: Optional[Tuple[str, str]] = None,
        outerJoin: Optional[Tuple[str, str]] = None,
    ) -> List[Any]:
        """Execute a query for the given table.

        Args:
            table (str): table to query
            columns: (List[str], optional): list of columns to select. Defaults to None (meaning all columns: *).
            where (str, optional): condition(s) to filter with WHERE. Defaults to None.
            orderByAsc (str, optional): column name to ascendingly order by. Defaults to None.
            orderByDesc (str, optional): column name to descendingly order by. Defaults to None.
            limit (int, optional): limit number results. Defaults to None.
            innerJoin (Tuple[str, str], optional): tuple where first element is table
                to join and second element is the column to INNER join on. Defaults to (None, None).
            outerJoin (Tuple[str, str], optional): tuple where first element is table
                to join and second element is the column to OUTER join on. Only supports LEFT OUTER JOIN.
                Defaults to (None, None).

        Raises:
            TypeError: if caller specifies multiple parameters that are not compatible with one another.

        Returns:
            List[Any]: List of rows returned by the query
        """
        if table not in self._tables:
            return []
        if innerJoin and innerJoin[0] not in self._tables:
            return []
        if outerJoin and outerJoin[0] not in self._tables:
            return []

        if innerJoin and outerJoin:
            raise TypeError("Query specified both innerJoin and outerJoin.")

        if orderByAsc and orderByDesc:
            raise TypeError("Query specified both orderByAsc and orderByDesc.")

        cur = self._db.cursor()

        columnsStr = ", ".join(columns) if columns else "*"
        where = f"WHERE {where}" if where else ""
        orderByAsc = f"ORDER BY {orderByAsc} ASC" if orderByAsc else ""
        orderByDesc = f"ORDER BY {orderByDesc} DESC" if orderByDesc else ""
        limitStr = f"LIMIT {limit}" if limit else ""
        innerJoinStr = (
            (f"INNER JOIN {innerJoin[0]} ON {table}.{innerJoin[1]}={innerJoin[0]}.{innerJoin[1]}")
            if innerJoin
            else ""
        )
        outerJoinStr = (
            (
                f"LEFT OUTER JOIN {outerJoin[0]} ON {table}.{outerJoin[1]}={outerJoin[0]}.{outerJoin[1]}"
            )
            if outerJoin
            else ""
        )

        cur.execute(
            f"SELECT {columnsStr} FROM {table} {innerJoinStr} {outerJoinStr} {where} {orderByAsc} {orderByDesc} {limitStr}"
        )

        return cur.fetchall()

    def _createDatatypesFromQuery(
        self: Reader, datatype: Type[Any], table: str, **kwargs: Any
    ) -> List[Any]:
        results = []
        # Key-value pair where the class instance variable name are the keys, and types are the values
        datatypeFields: dict = {}
        # Set of key/column names common between datatype and DB table
        commonFields: Set[str] = set()

        for row in self._query(table, **kwargs):
            if not datatypeFields:
                datatypeFields = {field.name: field.type for field in dataclasses.fields(datatype)}
                commonFields = set(row.keys()).intersection(datatypeFields.keys())

            instance = datatype(
                **{
                    field: row[field]
                    if datatypeFields[field] != "datetime64"
                    else rsktime2datetime(row[field])
                    for field in commonFields
                }
            )
            results.append(instance)

        return results

    def instrument(self: Reader) -> Optional[Instrument]:
        """Get a single instrument from the 'instruments' table.
        Filters for the instrument with the smallest instrumentID.
        """
        datatype, table = Instrument, "instruments"
        results = self._createDatatypesFromQuery(
            datatype, table, orderByAsc="instrumentID", limit=1
        )
        return results[0] if results else None  # type: ignore

    def instruments(self: Reader) -> List[Instrument]:
        f"""Get all instruments from the 'instruments' table."""
        datatype, table = Instrument, "instruments"
        return self._createDatatypesFromQuery(datatype, table, orderByAsc="instrumentID")

    def deployment(self: Reader) -> Optional[Deployment]:
        """Get a single deployment from the 'deployments' table.
        Filters for the deployment with the smallest instrumentID (foreign key).
        """
        datatype, table = Deployment, "deployments"
        results = self._createDatatypesFromQuery(
            datatype, table, orderByAsc="instrumentID", limit=1
        )
        return results[0] if results else None  # type: ignore

    def deployments(self: Reader) -> List[Deployment]:
        """Get all deployments from the 'deployments' table."""
        datatype, table = Deployment, "deployments"
        return self._createDatatypesFromQuery(datatype, table)

    def channels(self: Reader) -> List[Channel]:
        """Get all channels from the 'channels' table."""
        datatype, table = Channel, "channels"

        # NOTE: Below is a slightly modified version of _createDatatypesFromQuery()

        results = []
        # Key-value pair where the class instance variable name are the keys, and types are the values
        datatypeFields: dict = {}
        # Set of key/column names common between datatype and DB table
        commonFields: Set[str] = set()
        # Keep track of how many times we have hit a specific channel name
        longNamesCount = {}
        for row in self._query(table):
            if not datatypeFields:
                datatypeFields = {field.name: field.type for field in dataclasses.fields(datatype)}
                commonFields = set(row.keys()).intersection(datatypeFields.keys())

            fields = {
                field: row[field]
                if datatypeFields[field] != "datetime64"
                else rsktime2datetime(row[field])
                for field in commonFields
            }
            fields["_dbName"] = fields["longName"]
            longName = formatchannelname(fields["_dbName"])
            if longName not in longNamesCount:
                longNamesCount[longName] = 0
            else:
                longNamesCount[longName] += 1
                longName = f"{longName}{longNamesCount[longName]}"
            fields["longName"] = longName

            instance = datatype(**fields)
            results.append(instance)

        return results

    def diagnosticsChannels(self: Reader) -> List[DiagnosticsChannels]:
        """Get all diagnostics channels from the 'diagnostics_channels' table."""
        datatype, table = DiagnosticsChannels, "diagnostics_channels"
        return self._createDatatypesFromQuery(datatype, table, orderByAsc="Id")

    def diagnosticsData(self: Reader) -> List[DiagnosticsData]:
        """Get all diagnostics data from the 'diagnostics_data' table."""
        datatype, table = DiagnosticsData, "diagnostics_data"
        return self._createDatatypesFromQuery(datatype, table)

    def geoData(self: Reader) -> List[GeoData]:
        """Get all geodata from the 'geodata' table."""
        datatype, table = GeoData, "geodata"
        return self._createDatatypesFromQuery(datatype, table)

    def epoch(self: Reader) -> Optional[Epoch]:
        """Get a single epoch from the 'epochs' table.
        Filters for the epoch with the smallest deploymentID (foreign key)."""
        datatype, table = Epoch, "epochs"
        results = self._createDatatypesFromQuery(
            datatype, table, orderByAsc="deploymentID", limit=1
        )
        return results[0] if results else None  # type: ignore

    def epochs(self: Reader) -> List[Epoch]:
        """Get all epochs from the 'epochs' table."""
        datatype, table = Epoch, "epochs"
        return self._createDatatypesFromQuery(datatype, table)

    def schedule(self: Reader) -> Optional[Schedule]:
        """Get a single schedule from the 'schedules' table.
        Filters for the schedule with the largest scheduleID."""
        datatype, table = Schedule, "schedules"
        results = self._createDatatypesFromQuery(datatype, table, orderByDesc="scheduleID", limit=1)
        return results[0] if results else None  # type: ignore

    def scheduleInfo(
        self: Reader, schedule: Optional[Schedule]
    ) -> Optional[
        Union[WaveInfo, ContinuousInfo, DirectionalInfo, BurstInfo, TideInfo, AverageInfo]
    ]:
        """Get the appropriate information relating to the given schedule."""
        if not schedule:
            return None

        if schedule.mode == "wave":
            datatype, table = WaveInfo, "wave"
        elif schedule.mode == "continuous":
            datatype, table = ContinuousInfo, "continuous"  # type: ignore
        elif schedule.mode == "burst":
            datatype, table = BurstInfo, "burst"  # type: ignore
        elif schedule.mode == "tide":
            datatype, table = TideInfo, "tide"  # type: ignore
        elif schedule.mode == "average":
            datatype, table = AverageInfo, "average"  # type: ignore
        elif schedule.mode == "ddsampling":
            datatype, table = DirectionalInfo, "directional"  # type: ignore
        else:
            return None

        results = self._createDatatypesFromQuery(
            datatype, table, where=f"scheduleID={schedule.scheduleID}", limit=1
        )
        return results[0] if results else None  # type: ignore

    def power(self: Reader) -> List[Power]:
        """Get all power values from the 'power' table."""
        datatype, table = Power, "power"
        return self._createDatatypesFromQuery(datatype, table)

    @abstractmethod
    def calibrations(self: Reader) -> List[Calibration]:
        """Get all calibration values from the 'calibrations' table."""
        # See child classes.
        raise NotImplementedError()

    def parameters(self: Reader) -> List[Parameter]:
        """Get all parameters from the 'parameters' table."""
        datatype, table = Parameter, "parameters"
        return self._createDatatypesFromQuery(datatype, table)

    def parameterKeys(self: Reader) -> List[ParameterKey]:
        """Get everything from the 'parameterKeys' table."""
        datatype, table = ParameterKey, "parameterKeys"
        return self._createDatatypesFromQuery(datatype, table)

    def appSettings(self: Reader) -> List[AppSetting]:
        """Get everything from the 'appSettings' table."""
        datatype, table = AppSetting, "appSettings"
        return self._createDatatypesFromQuery(datatype, table)

    def ranging(self: Reader) -> List[Range]:
        """Get everything from the 'ranging' table."""
        datatype, table = Range, "ranging"
        return self._createDatatypesFromQuery(datatype, table)

    def instrumentSensors(self: Reader) -> List[InstrumentSensor]:
        """Get everything from the 'instrumentSensors' table."""
        datatype, table = InstrumentSensor, "instrumentSensors"
        return self._createDatatypesFromQuery(datatype, table)

    def instrumentChannels(self: Reader) -> List[InstrumentChannel]:
        """Get everything from the 'instrumentChannels' table."""
        datatype, table = InstrumentChannel, "instrumentChannels"
        return self._createDatatypesFromQuery(datatype, table)

    def regions(
        self,
    ) -> List[
        Union[
            RegionCal,
            RegionCast,
            RegionComment,
            RegionExclude,
            RegionGeoData,
            RegionPlateau,
            RegionProfile,
            RegionAtmosphere,
        ]
    ]:
        """Get all regions from the 'region' table and all subtables related to it."""
        results = []
        parentTable = "region"

        for childClass, mapping in self.REGION_TYPE_MAPPING.items():
            childTable = mapping["table"]
            regionType = mapping["type"]

            columns: Set[str] = {field.name for field in dataclasses.fields(childClass)}
            columns.discard("type")
            columns.add(f"{parentTable}.type")
            columns.discard("regionID")
            columns.add(f"{parentTable}.regionID")
            if regionType == "CAST" or regionType == "EXCLUSION":
                columns.discard("regionType")
                columns.add(f"{childTable}.type as regionType")

            for row in self._query(
                parentTable,
                columns=columns,
                outerJoin=(childTable, "regionID"),
                where=f'{parentTable}.type="{regionType}"',
            ):
                instance = childClass(
                    **{
                        field: row[field]
                        if field != "tstamp1" and field != "tstamp2"
                        else rsktime2datetime(row[field])
                        for field in row.keys()
                    }
                )
                results.append(instance)

        return results

    def _data(
        self, table: str, channels: List[Channel], startTime: np.datetime64, endTime: np.datetime64
    ) -> npt.NDArray:
        t1, t2 = datetime2rsktime(startTime), datetime2rsktime(endTime)
        channelRe = re.compile(r"channel(\d+)")

        # Because we are returning a Numpy array, let's always create the array dtype
        # for consistency sake. To do that, we need the columns before anything.
        columns = self._getTableColumns(table)
        queryColumns = ["tstamp"]
        # From columns and given channels, create the dtype
        types = [("timestamp", "datetime64[ms]")]
        channelIDs = set([c.channelID for c in channels])
        for key in columns:
            if match := channelRe.match(key):
                channelID = int(match.group(1))
                if channelID in channelIDs:
                    channelName = [c.longName for c in channels if c.channelID == channelID]
                    types.append((channelName[0], "float64"))
                    queryColumns.append(key)

        rows = self._query(
            table,
            columns=queryColumns,
            where=f"tstamp BETWEEN {t1} AND {t2}",
            orderByAsc="tstamp",
        )
        if not rows:
            return np.array([], dtype=types)

        return np.fromiter(
            ((rsktime2datetime(r[0]), *r[1:]) for r in rows), dtype=types, count=len(rows)
        )

    def data(
        self, channels: List[Channel], startTime: np.datetime64, endTime: np.datetime64
    ) -> npt.NDArray:
        """Get all data from the 'data' table.

        Args:
            startTime (int): start time in ms.
            endTime (int): end time in ms.
        """
        table = "data"

        return self._data(table, channels, startTime, endTime)

    def processedData(
        self, channels: List[Channel], startTime: np.datetime64, endTime: np.datetime64
    ) -> npt.NDArray:
        """Get all burst data from the 'burstData' or (in newer RSK version) 'processedData<type>` table(s)."""
        table = "burstData"

        return self._data(table, channels, startTime, endTime)
