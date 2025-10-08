#!/usr/bin/env python3
"""
pyRSKtools is a simple Python toolbox to open RSK SQLite files generated
by RBR instruments.
"""
# Standard/external imports
from __future__ import annotations
from typing import *
from typing import TYPE_CHECKING
from types import TracebackType
from dataclasses import dataclass, is_dataclass
import sqlite3
import numpy as np
import numpy.typing as npt

# Module imports (also serve as exports in this case)
from . import datatypes
from . import utils
from . import channels

# Module imports needed for type checking only (i.e., not exported)
if TYPE_CHECKING:
    from .readers import Reader
    from .datatypes import *

__copyright__ = "Copyright (c) 2022 RBR Ltd."
__version__ = "1.1.2"
__all__ = ["RSK", "datatypes", "utils", "channels"]


class RSK:
    from ._rsk.read import (  # type: ignore
        open,
        readdata,
        computeprofiles,
        getprofilesindices,
        getprofilesindicessortedbycast,
        getdataseriesindices,
        readprocesseddata,
        csv2rsk,
        close,
    )
    from ._rsk.calculators import (  # type: ignore
        derivesalinity,
        deriveseapressure,
        derivedepth,
        derivevelocity,
        deriveC25,
        deriveBPR,
        deriveO2,
        derivebuoyancy,
        derivesigma,
        deriveSA,
        derivetheta,
        derivesoundspeed,
        deriveA0A,
        deriveAPT,
    )
    from ._rsk.post_processors import (  # type: ignore
        calculateCTlag,
        alignchannel,
        binaverage,
        correcthold,
        despike,
        smooth,
        removeloops,
        trim,
        correctTM,
        correcttau,
        generate2D,
        centrebursttimestamp,
    )
    from ._rsk.view import (  # type: ignore
        plotdata,
        plotprofiles,
        images,
        plotTS,
        plotprocesseddata,
        mergeplots,
    )
    from ._rsk.export import RSK2CSV, RSK2RSK  # type: ignore
    from ._rsk.other import (  # type: ignore
        copy,
        create,
        addchannel,
        removecasts,
        appendlog,
        printchannels,
        getregionsbytypes,
    )

    # Extra/private methods (i.e., not relevant to end-users)
    from ._rsk.calculators import _deriveconcentration, _derivesaturation  # type: ignore
    from ._rsk._utils import (  # type: ignore
        printwarning,
        dataexistsorerror,
        getprofilesorerror,
        channelexists,
        channelsexistorerror,
        appendchannel,
        getchannelnamesandunits,
        getdbnamesfromlongnames,
    )

    # Set class methods
    csv2rsk = classmethod(csv2rsk)
    create = classmethod(create)

    # Set static methods
    printwarning = staticmethod(printwarning)
    mergeplots = staticmethod(mergeplots)

    def __init__(self: RSK, fname: str, readHiddenChannels: bool = False) -> None:
        """The class used to interact with an RSK dataset produced by Ruskin.

        Args:
            fname (str): file name of the RSK dataset.
            readHiddenChannels (bool, optional): read hidden channels when set as True. Defaults to False.

        **Internal state attributes:**

        Attributes:
            filename (str): File name of the RSK dataset.
            version (str): The current pyRSKtools version.
            logs (Dict[np.datetime64, str]): A dictionary for holding logs of the major actions/methods conducted/invoked
                during the lifetime of the current RSK instance. The key of each element is the time the log was generated,
                while the value is the log entry itself. Defaults to {}.

        **Informational attributes:**

        Attributes:
            dbInfo (DbInfo): Information about the opened dataset, e.g., version and type. Defaults to None.
            instrument (Instrument): Instrument of the dataset. Defaults to None.
            deployment (Deployment): Deployment header information. Defaults to None.
            channels (List[Channel]): A list of instrument channels. Defaults to [].
            diagnosticsChannels (List[DiagnosticsChannels]): Diagnostics channel name and unit information. Defaults to [].
            diagnosticsData (List[DiagnosticsData]): Diagnostics information containing battery and time synchronization. Defaults to [].
            epoch (Epoch): The dataset epoch times. Defaults to None.
            schedule (Schedule): Instrument schedule information. Defaults to None.
            scheduleInfo (ScheduleInfo): Information relating to the instrument schedule,
                changes depending on the ``mode`` field of :obj:`.RSK.schedule`. Defaults to None.
            power (List[Power]): Power information of the current deployment. Defaults to [].
            calibrations (List[Calibration]): Instrument calibration information. Defaults to [].
            parameters (List[Parameter]): Parameter header. Defaults to [].
            parameterKeys (List[ParameterKey]): Keys relating to :obj:`.RSK.parameters`. Defaults to [].
            appSettings (List[AppSetting]): Metadata about the current dataset. Defaults to [].
            ranging (List[Range]): Instrument range/gain information. Defaults to [].
            instrumentSensors (List[InstrumentSensor]): Instrument sensor information. Defaults to [].
            instrumentChannels (List[InstrumentChannel]): Instrument channel order and status information. Defaults to [].
            regions (Tuple[Region]): Dataset regions. Note, this field is an immutable tuple,
                please see :meth:`.RSK.removecasts` to remove cast type regions. Defaults to ().

        **Computational attributes:**

        Attributes:
            channelNames (List[str]): The channel names of :obj:`.RSK.data`, excluding "timestamp", used to index into :obj:`.RSK.data`.
            data (npt.NDArray): A structured NumPY array containing sample data of the current dataset.
                Populated by :obj:`.RSK.readdata`. Defaults to [].
            processedChannelNames (List[str]): The channel names of :obj:`.RSK.processedData`, excluding "timestamp",
                used to index into :obj:`.RSK.processedData`.
            processedData (npt.NDArray): A structured NumPY array containing processed sample data of the current dataset.
                Populated by :obj:`.RSK.readprocesseddata`. Defaults to [].

        Example:

            >>> with RSK("/path/to/data.rsk") as rsk:
            ...     # Read, process, view, or export data here
            ...     rsk.readdata()
        """
        # ----- Private attributes -----
        self._db: sqlite3.Connection = None
        self._reader: Reader = None
        self._readHiddenChannels = readHiddenChannels
        # See the `regions` property below for the publicly accesible version of this.
        self._regions: Tuple[
            Union[
                RegionCal,
                RegionCast,
                RegionComment,
                RegionExclude,
                RegionGeoData,
                RegionPlateau,
                RegionProfile,
            ]
        ] = None

        # ----- Public internal state attributes -----
        self.filename: str = fname
        self.version = __version__
        self.logs: Dict[np.datetime64, str] = {}

        # ----- Public informational attributes -----
        self.dbInfo: Optional[DbInfo] = None
        self.instrument: Optional[Instrument] = None
        self.deployment: Optional[Deployment] = None
        self.channels: List[Channel] = []
        self.epoch: Optional[Epoch] = None
        self.schedule: Optional[Schedule] = None
        self.scheduleInfo: Optional[ScheduleInfo] = None
        self.power: List[Power] = []
        self.calibrations: List[Calibration] = []
        self.parameters: List[Parameter] = []
        self.parameterKeys: List[ParameterKey] = []
        self.appSettings: List[AppSetting] = []
        self.ranging: List[Range] = []
        self.instrumentSensors: List[InstrumentSensor] = []
        self.instrumentChannels: List[InstrumentChannel] = []
        self.diagnosticsChannels: List[DiagnosticsChannels] = []
        self.diagnosticsData: List[DiagnosticsData] = []
        self.geoData: List[GeoData] = []

        # ----- Public computational attributes -----
        self.data: npt.NDArray = np.array([])
        self.processedData: npt.NDArray = np.array([])

    def __enter__(self: RSK) -> RSK:
        self.open()
        return self

    def __exit__(
        self: RSK,
        exc_type: Optional[BaseException],
        exc_value: Optional[BaseException],
        exc_traceback: Optional[TracebackType],
    ) -> None:
        self.close()

    def __str__(self: RSK) -> str:
        attrs = {attr for attr in self.__dict__.keys() if not attr.startswith("_")}
        internalStateAttrs = {"filename", "version", "logs"}
        computationalAttrs = {"data", "processedData"}
        dataAttrs = (attrs - internalStateAttrs) - computationalAttrs
        # Regions is a special case because it is hidden under a getter method.
        dataAttrs.add("regions")
        sections = [
            {
                "title": "Internal state attributes",
                "attributes": sorted(internalStateAttrs),
            },
            {"title": "Informational attributes", "attributes": sorted(dataAttrs)},
            {"title": "Computational attributes", "attributes": sorted(computationalAttrs)},
        ]

        s = f"RSK\n"
        for section in sections:
            s += f"  {section['title']}:\n"
            for attr in section["attributes"]:
                attr_value = getattr(self, attr)
                attr_state = "unpopulated"

                if "Computational" in section["title"]:
                    if attr_value.size > 0:
                        attr_state = f"populated with {attr_value.size} elements"
                elif attr_value:
                    if (
                        isinstance(attr_value, list)
                        or isinstance(attr_value, dict)
                        or attr == "regions"
                    ):
                        attr_state = f"populated with {len(attr_value)} elements"
                    else:
                        attr_state = "populated"

                s += f"    .{attr} is {attr_state}\n"

        return s

    @property
    def channelNames(self: RSK) -> List[str]:
        """The channel names of RSK.data, excluding "timestamp", are used to index into RSK.data."""
        if self.data.size == 0:
            # self.printwarning("RSK.data is empty. Make sure to call RSK.readdata() first!")
            return []

        return list(self.data.dtype.names[1:])

    @property
    def processedChannelNames(self: RSK) -> List[str]:
        """The channel names of RSK.processedData, excluding "timestamp", are used to index into RSK.processedData."""
        if self.processedData.size == 0:
            # self.printwarning(
            #     "RSK.processedData is empty. Make sure to call RSK.readprocesseddata() first!"
            # )
            return []

        return list(self.processedData.dtype.names[1:])

    @property
    def regions(self: RSK):  # type: ignore
        return self._regions

    @regions.setter
    def regions(
        self: RSK,
        regions: List[
            Union[
                RegionCal,
                RegionCast,
                RegionComment,
                RegionExclude,
                RegionGeoData,
                RegionPlateau,
                RegionProfile,
            ]
        ],
    ) -> None:
        """When trying to set the `regions` property, sort the given list then
        cast it into a tuple before setting the internal private instance variable.
        """
        regions.sort(
            key=lambda x: (x.tstamp2, x.type)
        )  # first sorted by tstamp2, then sorted by type to ensure CAST listed in front of PROFILE
        self._regions = tuple(regions)  # type: ignore


if __name__ == "__main__":
    with RSK("../test.rsk") as rsk:
        pass
