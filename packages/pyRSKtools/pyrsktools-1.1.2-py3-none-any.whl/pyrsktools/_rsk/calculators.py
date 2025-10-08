#!/usr/bin/env python3
# Standard/external imports
from __future__ import annotations
from typing import *
import numpy as np
import numpy.ma as ma
import numpy.typing as npt
import gsw
from scipy import interpolate
import re

# Module imports
from pyrsktools.datatypes import *
from pyrsktools.channels import *
from pyrsktools import utils
from pyrsktools.readers import RSKFullReader

if TYPE_CHECKING:
    from pyrsktools import RSK


def derivesalinity(self: RSK, seawaterLibrary: str = "TEOS-10") -> None:
    """Calculate practical salinity.

    Args:
        seawaterLibrary (str, optional): which underlying library this method should utilize. Current support includes: "TEOS-10".
            Defaults to "TEOS-10".

    Calculates salinity from measurements of conductivity, temperature, and sea pressure, using the TEOS-10 GSW function ``gsw_SP_from_C``.
    The result is added to the :obj:`.RSK.data` field of the current RSK instance, and metadata in :obj:`.RSK.channels` is updated.
    It requires the current RSK instance to be populated with conductivity, temperature, and pressure data.

    If there is already a salinity channel present, this method replaces the values with a new calculation of salinity.

    If sea pressure is not present, this method calculates it with the default atmospheric pressure, usually 10.1325 dbar.
    We suggest using :meth:`RSK.deriveseapressure` before this for customizable atmospheric pressure.

    Example:

    >>> rsk.derivesalinity()
    ... # Optional arguments
    ... rsk.derivesalinity(seawaterLibrary="TEOS-10")
    """
    self.dataexistsorerror()
    self.channelsexistorerror([Conductivity, Temperature])

    if not self.channelexists(SeaPressure):
        self.deriveseapressure()

    if seawaterLibrary == "TEOS-10":
        salinity = gsw.SP_from_C(
            self.data[Conductivity.longName],
            self.data[Temperature.longName],
            self.data[SeaPressure.longName],
        )
    else:
        raise ValueError(f"Invoked with unsupported seawater library: {seawaterLibrary}")

    self.appendchannel(Salinity, salinity, 0, 1)
    self.appendlog(f"Practical Salinity derived using {seawaterLibrary} library")


def deriveseapressure(self: RSK, patm: Optional[Union[float, Collection[float]]] = None) -> None:
    """Calculate sea pressure.

    Args:
        patm (Union[float, Collection[float]], optional): atmosphere pressure for calculating the sea pressure. Defaults to None (see below).

    Calculates sea pressure from pressure and atmospheric pressure.
    The result is added to the :obj:`.RSK.data` field of the current RSK instance, and metadata in :obj:`.RSK.channels` is updated.
    It requires the current RSK instance to be populated with pressure data.

    The ``patm`` argument is the atmospheric pressure used to calculate the sea pressure.
    A custom value can be used; otherwise, the default is to retrieve the value stored in the parameters field
    or to assume it is 10.1325 dbar if the parameters field is unavailable.
    This method also supports a variable ``patm`` input as a list, when that happens,
    the input list should have the same length as :obj:`.RSK.data`.

    If there is already a sea pressure channel present, the function replaces the values with the new calculation of
    sea pressure based on the values currently in the pressure column.

    Example:

    >>> rsk.deriveseapressure()
    ... # Optional arguments
    ... rsk.deriveseapressure(patm=10.1)
    """
    self.dataexistsorerror()

    # Determine patm (atmospheric pressure)
    if not hasattr(patm, "__len__"):
        # If not passed in, first try to find a valid value in parameterKeys
        if not patm:
            for param in self.parameterKeys:
                if param.key == "ATMOSPHERE":
                    patm = float(param.value)  # ParameterKey.value is a string

        # If patm exsists, make sure it has been cast to a float.
        # If it doesn't exist (i.e., not passed in and not found in parameterKeys), set default value
        patm = float(patm) if patm else 10.1325  # type: ignore
    else:  # If the user passed in a list for patm, check its length
        if len(patm) != len(self.data):  # type: ignore
            raise ValueError(
                f"Expected input patm length ({len(patm)}) to be the same as RSK.data length ({len(self.data)})"  # type: ignore
            )

    if self.channelexists(Pressure):
        seapressure = self.data[Pressure.longName] - patm
    elif self.channelexists(BprPressure):
        seapressure = self.data[BprPressure.longName] - patm
    else:
        self.printwarning("No pressure channel available, sea pressure will be set to 0.")
        seapressure = np.zeros(self.data.size, "float64")

    self.appendchannel(SeaPressure, seapressure, 0, 1)

    if hasattr(patm, "__len__"):
        self.appendlog("Sea pressure calculated using variable atmospheric pressure values.")
    else:
        self.appendlog(f"Sea pressure calculated using an atmospheric pressure of {patm} dbar.")


def derivedepth(self: RSK, latitude: float = 45.0, seawaterLibrary: str = "TEOS-10") -> None:
    """Calculate depth from pressure.

    Args:
        latitude (float, optional): latitude of the pressure measurement in decimal degrees. Defaults to 45.0.
        seawaterLibrary (str, optional): which underlying library this method should utilize. Current support includes: "TEOS-10". Defaults to "TEOS-10".

    Calculates depth from pressure.
    The result is added to the :obj:`.RSK.data` field of the current RSK instance, and metadata in :obj:`.RSK.channels` is updated.
    If there is already a depth channel present, this method replaces the values with the new calculation of depth.

    If sea pressure is not present in the current RSK instance, it is calculated with the default atmospheric pressure (10.1325 dbar)
    by :meth:`.RSK.deriveseapressure` before deriving salinity when a different value of atmospheric pressure is used.

    Example:

    >>> rsk.derivedepth()
    ... # Optional arguments
    ... rsk.derivedepth(latitude=45.34, seawaterLibrary="TEOS-10")
    """
    self.dataexistsorerror()
    self.channelsexistorerror([SeaPressure])

    if not self.channelexists(SeaPressure):
        self.deriveseapressure()

    if seawaterLibrary == "TEOS-10":
        depth = -gsw.z_from_p(self.data[SeaPressure.longName], latitude)
    else:
        raise ValueError(f"Invoked with unsupported seawater library: {seawaterLibrary}")

    self.appendchannel(Depth, depth, 0, 1)
    self.appendlog(
        f"Depth calculated using the {seawaterLibrary} library and a latitude of {latitude} degrees"
    )


def derivevelocity(self: RSK, windowLength: int = 3) -> None:
    """Calculate velocity from depth and time.

    Args:
        windowLength (int, optional): length of the filter window used for the reference salinity. Defaults to 3.

    Calculates profiling velocity from depth and time.
    The result is added to the :obj:`.RSK.data` field of the current RSK instance, and metadata in :obj:`.RSK.channels` is updated.
    It requires the current RSK instance to be populated with depth (see :meth:`.RSK.derivedepth`).
    The depth channel is smoothed with a running average of length windowLength to reduce noise,
    and then the smoothed depth is differentiated with respect to time to obtain a profiling speed.

    If there is already a velocity channel present, this method replaces the velocity values with the new calculation.

    If there is not a velocity channel but depth is present, this method adds the velocity channel metadata
    to :obj:`.RSK.channels` and calculates velocity based on the values in the depth column.

    Example:

    >>> rsk.derivevelocity()
    ... # Optional arguments
    ... rsk.derivevelocity(windowLength=5)
    """
    self.dataexistsorerror()
    self.channelsexistorerror([Depth])

    depth = utils.runavg(self.data[Depth.longName], windowLength, "nan")
    velocity = utils.calculatevelocity(depth, self.data["timestamp"])

    self.appendchannel(Velocity, velocity, 0, 1)
    self.appendlog(
        f"Profiling velocity calculated from depth, filtered with a windowLength of {windowLength} samples."
    )


def deriveC25(self: RSK, alpha: float = 0.0191) -> None:
    """Calculate specific conductivity at 25 degrees Celsius in units of mS/cm.

    Args:
        alpha (float, optional):  temperature sensitivity coefficient. Defaults to 0.0191 deg C⁻¹.

    Computes the specific conductivity in µS/cm at 25 degrees Celsius given the conductivity in mS/cm and temperature in degrees Celsius.
    The result is added to the :obj:`.RSK.data` field of the current RSK instance, and metadata in :obj:`.RSK.channels` is updated.

    The calculation uses the Standard Methods for the Examination of Water and Waste Water (eds. Clesceri et. al.), 20th edition, 1998.
    The default temperature sensitivity coefficient, alpha, is 0.0191 deg C-1. Considering that the coefficient can range depending on
    the ionic composition of the water. The coefficient is made customizable.

    Example:

    >>> rsk.deriveC25()
    ... # Optional arguments
    ... rsk.deriveC25(alpha=0.0191)
    """
    self.dataexistsorerror()
    self.channelsexistorerror([Conductivity, Temperature])

    conductivity = self.data[Conductivity.longName]
    temperature = self.data[Temperature.longName]
    # Derive specific conductivity
    specificConductivity = conductivity / (1 + alpha * (temperature - 25))
    specificConductivity *= 1000  # Convert unit from mS/cm to µS/cm

    self.appendchannel(SpecificConductivity, specificConductivity, 0, 1)
    self.appendlog(
        f"Specific conductivity at 25 degrees Celsius derived using a temperature sensitivity coefficient of {alpha} deg C⁻¹."
    )


def deriveBPR(self: RSK) -> None:
    """Convert bottom pressure recorder frequencies to temperature and pressure using calibration coefficients.

    Loggers with bottom pressure recorder (BPR) channels are equipped with a Paroscientific, Inc. pressure transducer.
    The logger records the temperature and pressure output frequencies from the transducer. RSK files of type ``full`` contain only
    the frequencies, whereas RSK files of type ``EPdesktop`` contain the transducer frequencies for pressure and temperature, as well
    as the derived pressure and temperature.

    This method derives temperature and pressure from the transducer frequency channels for ``full`` files. It implements the
    calibration equations developed by Paroscientific, Inc. to derive pressure and temperature.
    Both results are added to the :obj:`.RSK.data` field of the current RSK instance, and metadata in :obj:`.RSK.channels` is updated.

    Example:

    >>> rsk.deriveBPR()
    """
    self.dataexistsorerror()

    if self.dbInfo.type != RSKFullReader.TYPE:
        raise ValueError(
            f"Only files of type '{RSKFullReader.TYPE}' need derivation for BPR pressure and temperature"
        )

    parosPCal = [c for c in self.calibrations if c.equation == "deri_bprpres"]
    parosTCal = [c for c in self.calibrations if c.equation == "deri_bprtemp"]

    assert len(parosPCal) == len(parosTCal)

    # Total number of Paros sensors (BPR and barometer)
    nParos = len(parosPCal)
    nBPR = sum(
        (1 for c in self.channels if c.longName.startswith(BprPressure.longName))
    )  # Total number of (already existing) BPRs (updates further in loop)

    # Loop over sensors that require application of calibration coefficients.
    # Each Paros has two channels, P and T.
    for i in range(nParos):
        pCal, tCal = parosPCal[i], parosTCal[i]

        u0 = tCal.x[0]
        y1, y2, y3 = tCal.x[1], tCal.x[2], tCal.x[3]

        c1, c2, c3 = pCal.x[1], pCal.x[2], pCal.x[3]
        d1, d2 = pCal.x[4], pCal.x[5]
        t1, t2, t3, t4, t5 = pCal.x[6], pCal.x[7], pCal.x[8], pCal.x[9], pCal.x[10]

        # Get channel names relating to calibration data, then use them to index into self.data,
        # which are the measure periods for T and P
        pChannel = [c for c in self.channels if c.channelID == pCal.n[0]][0]
        tChannel = [c for c in self.channels if c.channelID == pCal.n[1]][0]
        presPeriod = self.data[pChannel.longName]
        tPeriod = self.data[tChannel.longName]

        # BPR temp and pres derivation calculations
        U = (tPeriod / (1e6)) - u0
        temp = y1 * U + y2 * U * U + y3 * U * U * U

        C = c1 + c2 * U + c3 * U * U
        D = d1 + d2 * U
        T0 = t1 + t2 * U + t3 * U * U + t4 * U * U * U + t5 * U * U * U * U
        Tsquare = (presPeriod / (1e6)) * (presPeriod / (1e6))
        Pres = C * (1 - ((T0 * T0) / (Tsquare))) * (1 - D * (1 - ((T0 * T0) / (Tsquare))))
        pres = Pres * 0.689476  # convert from PSI to dbar

        if pChannel.shortName == "peri00":
            derivedPChannel = BprPressure
        elif pChannel.shortName == "baro00":
            derivedPChannel = BarometerPressure
        elif pChannel.shortName == "peri02":
            derivedPChannel = BprPressure
        else:
            raise ValueError(f"Unknown pressure channel shortName: {pChannel.shortName}")

        if tChannel.shortName == "peri01":
            derivedTChannel = BprTemperature
        elif tChannel.shortName == "baro01":
            derivedTChannel = BarometerTemperature
        elif tChannel.shortName == "peri03":
            derivedTChannel = BprTemperature
        else:
            raise ValueError(f"Unknown temperature channel shortName: {tChannel.shortName}")

        if nParos > 1 and derivedPChannel == BprPressure:
            derivedPChannel = derivedPChannel.withnewname(f"{derivedPChannel.longName}{nBPR}")
            derivedTChannel = derivedTChannel.withnewname(f"{derivedTChannel.longName}{nBPR}")
            nBPR += 1

        self.appendchannel(derivedPChannel, pres, 0, 1)
        self.appendchannel(derivedTChannel, temp, 0, 1)

    self.appendlog("BPR temperature and pressure derived from period data.")


def _deriveconcentration(self: RSK, unit: str) -> None:
    validUnits = {"µmol/l", "ml/l", "mg/l"}

    # Normalize the input: replace 'u' with 'µ' and convert to lowercase
    unit = unit.lower().replace("u", "µ")

    if unit not in validUnits:
        raise ValueError(
            f"Invalid unit specified for O2 concentration calculation: {unit}. Expected one of: {', '.join(validUnits)}."
        )

    self.channelsexistorerror([Temperature, Salinity, DissolvedO2Saturation])

    temperature = self.data[Temperature.longName]
    salinity = self.data[Salinity.longName]
    saturation = self.data[DissolvedO2Saturation.longName]

    # Derive concentration using the Weiss equation.
    a1, a2, a3, a4 = -173.42920, 249.63390, 143.34830, -21.84920
    b1, b2, b3 = -0.0330960, 0.0142590, -0.00170

    temperature = (temperature * 1.00024 + 273.15) / 100.0
    concentration = (
        saturation
        * np.exp(
            a1
            + a2 / temperature
            + a3 * np.log(temperature)
            + a4 * temperature
            + salinity * (b1 + b2 * temperature + b3 * temperature * temperature)
        )
        / 100.0
    )
    # Weiss equation gives us concentration in ml/l, convert if necessary depending on unit
    if unit == "µmol/l":
        concentration *= 44.659
    elif unit == "mg/l":
        concentration *= 1.4276
    else:  # ml/l
        pass

    # Create custom channel instead of the hardcoded one from channels.py
    # that specifies the correct unit.
    channel = Channel(
        shortName="doxy27",
        longName="dissolved_o2_concentration",
        units=unit,
        _dbName="Dissolved O₂ concentration",
    )
    self.appendchannel(channel, concentration, 0, 1)
    self.appendlog(f"O2 concentration in units of {unit} derived from measured O2 saturation.")


def _derivesaturation(self: RSK) -> None:
    self.channelsexistorerror([Temperature, Salinity, DissolvedO2Concentration])
    # This should never fail if the DissolvedO2Concentration channel exists
    # in self.data (checked by channelsexistorerror() above)
    try:
        unit = [c.units for c in self.channels if c.longName == DissolvedO2Concentration.longName][
            0
        ]
    except Exception:
        raise ValueError(
            f'Channel required for calculation missing in RSK.channels: "{DissolvedO2Concentration.longName}"'
        )

    temperature = self.data[Temperature.longName]
    salinity = self.data[Salinity.longName]
    concentration = self.data[DissolvedO2Concentration.longName]

    # Derive saturation using the Gorcia and Gordon equation
    ga0, ga1, ga2, ga3, ga4, ga5 = 2.00856, 3.22400, 3.99063, 4.80299, 9.78188e-1, 1.71069
    gb0, gb1, gb2, gb3 = -6.24097e-3, -6.93498e-3, -6.90358e-3, -4.29155e-3
    gc0 = -3.11680e-7

    temperature = np.log((298.15 - temperature) / (273.15 + temperature))
    coef = np.exp(
        ga0
        + temperature
        * (
            ga1
            + temperature * (ga2 + temperature * (ga3 + temperature * (ga4 + ga5 * temperature)))
        )
        + salinity * (gb0 + temperature * (gb1 + temperature * (gb2 + temperature * gb3)))
        + salinity * salinity * gc0
    )

    if unit == "µmol/l":
        saturation = (2.2414) * concentration / coef
    elif unit == "ml/l":
        saturation = (2.2414 / 44.659) * concentration / coef
    elif unit == "mg/l":
        saturation = (1.4276 * 2.2414 / 44.659) * concentration / coef
    else:
        raise ValueError(f"Invalid/unsupported unit for O2 concentration: {unit}")

    self.appendchannel(DissolvedO2Saturation, saturation, 0, 1)
    self.appendlog(
        f"O2 saturation in units of {DissolvedO2Saturation.units} derived from measured O2 concentration."
    )


def deriveO2(self: RSK, toDerive: str = "concentration", unit: str = "µmol/l") -> None:
    """Derives dissolved oxygen concentration or saturation.

    Args:
        toDerive (str, optional):  O2 variable to derive, should only be "saturation" or "concentration". Defaults to "concentration".
        unit (str, optional): unit of derived O2 concentration, valid inputs include "µmol/l", "ml/l", or "mg/l". Defaults to "µmol/l".
            Only effective when toDerive is concentration.

    Derives dissolved O2 concentration from measured dissolved O2 saturation using R.F. Weiss (1970), or conversely,
    derives dissolved O2 saturation from measured dissolved O2 concentration using Garcia and Gordon (1992).
    The result is added to the :obj:`.RSK.data` field of the current RSK instance, and metadata in :obj:`.RSK.channels` is updated.

    References:
        * R.F. Weiss, The solubility of nitrogen, oxygen and argon in water and seawater, Deep-Sea Res., 17 (1970), pp. 721-735
        * H.E. Garc, L.I. Gordon, Oxygen solubility in seawater: Better fitting equations, Limnol. Oceanogr., 37 (6) (1992), pp. 1307-1312

    Example:

    >>> rsk.deriveO2()
    ... # Optional arguments
    ... rsk.deriveO2(toDerive="saturation", unit="ml/l")
    """
    self.dataexistsorerror()

    validDerives = {"concentration", "saturation"}
    if toDerive not in validDerives:
        raise ValueError(
            f"Invalid value for argument 'toDerive': {toDerive}. Expected one of: {', '.join(validDerives)}."
        )

    if toDerive == "concentration":
        self._deriveconcentration(unit)
    else:
        self._derivesaturation()


def derivebuoyancy(self: RSK, latitude: float = 45.0, seawaterLibrary: str = "TEOS-10") -> None:
    """Calculate buoyancy frequency N^2 and stability E.

    Args:
        latitude (float, optional):  latitude in decimal degrees north [-90 ... +90]. Defaults to 45.0.
        seawaterLibrary (str, optional): which underlying library this method should utilize. Current support includes: "TEOS-10". Defaults to "TEOS-10".

    Derives buoyancy frequency and stability using the TEOS-10 GSW toolbox library.
    The result is added to the :obj:`.RSK.data` field of the current RSK instance, and metadata in :obj:`.RSK.channels` is updated.

    .. note::

        The Absolute Salinity anomaly is taken to be zero to simplify the calculation.

    Example:

    >>> rsk.derivebuoyancy()
    ... # Optional arguments
    ... rsk.derivebuoyancy(latitude=45.34)
    """
    self.dataexistsorerror()
    self.channelsexistorerror([Temperature, Salinity, SeaPressure])

    temperature = self.data[Temperature.longName]
    salinity = self.data[Salinity.longName]
    seaPressure = self.data[SeaPressure.longName]

    # Calculate buoyancy frequency squared (N^2) and stability
    if seawaterLibrary == "TEOS-10":
        absoluteSalinity = gsw.SR_from_SP(salinity)  # Assume SA ~= SR
        conservativeTemperature = gsw.CT_from_t(absoluteSalinity, temperature, seaPressure)
        buoyancyMid, pressureMid = gsw.Nsquared(
            absoluteSalinity, conservativeTemperature, seaPressure, latitude
        )
        gravity = gsw.grav(latitude, seaPressure)
        buoyancy = interpolate.interp1d(
            ma.getdata(pressureMid),
            ma.getdata(buoyancyMid),
            kind="linear",
            fill_value="extrapolate",
        )(ma.getdata(seaPressure))
        stability = buoyancy / gravity
    else:
        raise ValueError(f"Invoked with unsupported seawater library: {seawaterLibrary}")

    self.appendchannel(BuoyancyFrequencySquared, buoyancy, 0, 1)
    self.appendchannel(Stability, stability, 0, 1)
    self.appendlog(
        f"Buoyancy frequency squared and stability derived using the {seawaterLibrary} library."
    )


def _deriveSA(
    salinity: npt.NDArray,
    seaPressure: npt.NDArray,
    latitude: Optional[Union[float, Collection[float]]] = None,
    longitude: Optional[Union[float, Collection[float]]] = None,
) -> npt.NDArray:
    # Assume _checkLatLong() has been caled before this,
    # that method ensures that if we have latitude we also have longitude
    hasCoord = True if hasattr(latitude, "__len__") or latitude else False

    if hasCoord:
        return gsw.SA_from_SP(salinity, seaPressure, longitude, latitude)  # type: ignore
    else:
        # Assume SA ~= SR
        return gsw.SR_from_SP(salinity)  # type: ignore


def _checkLatLong(
    data: npt.NDArray,
    latitude: Optional[Union[float, Collection[float]]],
    longitude: Optional[Union[float, Collection[float]]],
) -> None:
    """Validate latitude/longitude inputs.

    Rules:
    - If either latitude or longitude is a sequence, both must be sequences of equal length and match len(data).
    - If both are scalars, accept any numeric values including 0.
    - If one is provided and the other is None, raise a clear error.
    - If both are None, that's acceptable (coordinates absent).
    """

    def _is_sequence(x: Any) -> bool:
        return hasattr(x, "__len__") and not isinstance(x, (str, bytes))

    lat_is_seq = _is_sequence(latitude)
    lon_is_seq = _is_sequence(longitude)

    # Sequence handling
    if lat_is_seq or lon_is_seq:
        if not (lat_is_seq and lon_is_seq):
            raise ValueError("Type of latitude and longitude do not match")
        from typing import Sized, cast

        lat_len = len(cast(Sized, latitude))
        lon_len = len(cast(Sized, longitude))
        if lat_len != len(data):
            raise ValueError(
                f"Expected input latitude length ({lat_len}) to be the same as RSK.data length ({len(data)})"
            )
        if lon_len != len(data):
            raise ValueError(
                f"Expected input longitude length ({lon_len}) to be the same as RSK.data length ({len(data)})"
            )
        return

    # Scalar / None handling
    lat_missing = latitude is None
    lon_missing = longitude is None
    if lat_missing ^ lon_missing:
        if lat_missing:
            raise ValueError("Missing latitude values")
        else:
            raise ValueError("Missing longitude values")
    # Both None or both scalar: accept
    return


def derivesigma(
    self: RSK,
    latitude: Optional[Union[float, Collection[float]]] = None,
    longitude: Optional[Union[float, Collection[float]]] = None,
    seawaterLibrary: str = "TEOS-10",
) -> None:
    """Calculate potential density anomaly.

    Args:
        latitude (Union[float, Collection[float]], optional):  latitude(s) in decimal degrees north. Defaults to None.
        longitude (Union[float, Collection[float]], optional): longitude(s) in decimal degrees east. Defaults to None.
        seawaterLibrary (str, optional): which underlying library this method should utilize. Current support includes: "TEOS-10". Defaults to "TEOS-10".

    Derives potential density anomaly using the TEOS-10 GSW toolbox library.
    The result is added to the :obj:`.RSK.data` field of the current RSK instance, and metadata in :obj:`.RSK.channels` is updated.

    Note that this method also supports a variable latitude and longitude input as a list, when that happens,
    the input list should have the same length of :obj:`RSK.data`.

    The workflow of the function is as below:

    1. Calculate absolute salinity (SA)
        * When latitude and longitude data are available (from the optional input),
          this method will call ``SA = gsw_SA_from_SP(salinity,seapressure,lon,lat)``
        * When latitude and longitude data are absent, this method will call ``SA = gsw_SR_from_SP(salinity)`` assuming that reference
          salinity equals absolute salinity approximately.
    2. Calculate conservative temperature ``pt0 = gsw.CT_from_t(absoluteSalinity, temperature, seaPressure)``
    3. Calculate conservative density anomaly ``sigma0 = gsw.sigma0(absoluteSalinity, conservativeTemperature)``

    .. image:: /img/RSKderivedensityanomaly.png
        :scale: 100%
        :alt: derive sigma diagram

    Example:

    >>> rsk.derivesigma()
    ... # Optional arguments
    ... rsk.derivesigma(latitude=45.34, longitude=-75.91)
    """
    self.dataexistsorerror()
    self.channelsexistorerror([Temperature, Salinity, SeaPressure])
    _checkLatLong(self.data, latitude, longitude)

    temperature = self.data[Temperature.longName]
    salinity = self.data[Salinity.longName]
    seaPressure = self.data[SeaPressure.longName]

    if seawaterLibrary == "TEOS-10":
        if self.channelexists(AbsoluteSalinity):
            absoluteSalinity = self.data[AbsoluteSalinity.longName]
        else:
            absoluteSalinity = _deriveSA(salinity, seaPressure, latitude, longitude)

        conservativeTemperature = gsw.CT_from_t(absoluteSalinity, temperature, seaPressure)
        densityAnomaly = gsw.sigma0(absoluteSalinity, conservativeTemperature)
    else:
        raise ValueError(f"Invoked with unsupported seawater library: {seawaterLibrary}")

    self.appendchannel(DensityAnomaly, densityAnomaly, 0, 1)
    self.appendlog(f"Potential density anomaly derived using the {seawaterLibrary} library.")


def deriveSA(
    self: RSK,
    latitude: Optional[Union[float, Collection[float]]] = None,
    longitude: Optional[Union[float, Collection[float]]] = None,
    seawaterLibrary: str = "TEOS-10",
) -> None:
    """Calculate absolute salinity.

    Args:
        latitude (Union[float, Collection[float]]): latitude(s) in decimal degrees north.  Defaults to None.
        longitude (Union[float, Collection[float]]): longitude(s) in decimal degrees east.  Defaults to None.
        seawaterLibrary (str, optional): which underlying library this method should utilize. Current support includes: "TEOS-10". Defaults to "TEOS-10".

    Derives absolute salinity using the TEOS-10 GSW toolbox.
    The result is added to the :obj:`.RSK.data` field of the current RSK instance, and metadata in :obj:`.RSK.channels` is updated.
    The workflow of the function depends on if GPS information is available:

    1. When latitude and longitude data are available (from the optional input),
       this method will call ``SA = gsw_SA_from_SP(salinity,seapressure,lon,lat)``
    2. When latitude and longitude data are absent, this method will call ``SA = gsw_SR_from_SP(salinity)`` assuming that reference
       salinity equals absolute salinity approximately.

    .. note::

        The latitude/longitude input must be either a single value or a list with the same length of :obj:`.RSK.data`.

    Example:

    >>> rsk.deriveSA()
    ... # Optional arguments
    ... rsk.deriveSA(latitude=45.34, longitude=-75.91)
    """
    self.dataexistsorerror()
    self.channelsexistorerror([Salinity, SeaPressure])
    _checkLatLong(self.data, latitude, longitude)

    salinity = self.data[Salinity.longName]
    seaPressure = self.data[SeaPressure.longName]

    if seawaterLibrary == "TEOS-10":
        absoluteSalinity = _deriveSA(salinity, seaPressure, latitude, longitude)
    else:
        raise ValueError(f"Invoked with unsupported seawater library: {seawaterLibrary}")

    self.appendchannel(AbsoluteSalinity, absoluteSalinity, 0, 1)
    self.appendlog(f"Absolute salinity derived using the {seawaterLibrary} library.")


def derivetheta(
    self: RSK,
    latitude: Optional[Union[float, Collection[float]]] = None,
    longitude: Optional[Union[float, Collection[float]]] = None,
    seawaterLibrary: str = "TEOS-10",
) -> None:
    """Calculate potential temperature with a reference sea pressure of zero.

    Args:
        latitude (Union[float, Collection[float]]): latitude(s) in decimal degrees north.  Defaults to None.
        longitude (Union[float, Collection[float]]): longitude(s) in decimal degrees east.  Defaults to None.
        seawaterLibrary (str, optional): which underlying library this method should utilize. Current support includes: "TEOS-10". Defaults to "TEOS-10".

    Derives potential temperature using the TEOS-10 GSW toolbox library.
    The result is added to the :obj:`.RSK.data` field of the current RSK instance, and metadata in :obj:`.RSK.channels` is updated.
    The workflow of this method is as below:

    1. Calculate absolute salinity (SA)
        * When latitude and longitude data are available (from the optional input),
          this method will call ``SA = gsw_SA_from_SP(salinity,seapressure,lon,lat)``
        * When latitude and longitude data are absent, this method will call ``SA = gsw_SR_from_SP(salinity)`` assuming
          that reference salinity equals absolute salinity approximately.
    2. Calculate potential temperature ``pt0 = gsw_pt0_from_t(absolute salinity,temperature,seapressure)``

    .. note::

        The latitude/longitude input must be either a single value or a list with the same length of :obj:`.RSK.data`.


    Example:

    >>> rsk.derivetheta()
    ... # Optional arguments
    ... rsk.derivetheta(latitude=45.34, longitude=-75.91)
    """
    self.dataexistsorerror()
    self.channelsexistorerror([Temperature, Salinity, SeaPressure])
    _checkLatLong(self.data, latitude, longitude)

    temperature = self.data[Temperature.longName]
    salinity = self.data[Salinity.longName]
    seaPressure = self.data[SeaPressure.longName]

    if seawaterLibrary == "TEOS-10":
        if self.channelexists(AbsoluteSalinity):
            absoluteSalinity = self.data[AbsoluteSalinity.longName]
        else:
            absoluteSalinity = _deriveSA(salinity, seaPressure, latitude, longitude)

        potentialTemperature = gsw.pt0_from_t(absoluteSalinity, temperature, seaPressure)
    else:
        raise ValueError(f"Invoked with unsupported seawater library: {seawaterLibrary}")

    self.appendchannel(PotentialTemperature, potentialTemperature, 0, 1)
    self.appendlog(f"Potential temperature derived using the {seawaterLibrary} library.")


def _deriveUnesco(S: npt.NDArray, T: npt.NDArray, SP: npt.NDArray) -> npt.NDArray:
    a = np.array(
        [
            [1.389, -1.262e-2, 7.166e-5, 2.008e-6, -3.21e-8],
            [9.4742e-5, -1.2583e-5, -6.4928e-8, 1.0515e-8, -2.0142e-10],
            [-3.9064e-7, 9.1061e-9, -1.6009e-10, 7.994e-12, 0.0],
            [1.100e-10, 6.651e-12, -3.391e-13, 0.0, 0.0],
        ]
    )

    b = np.array(
        [
            [-1.922e-2, -4.42e-5],
            [7.3637e-5, 1.7950e-7],
        ]
    )

    c = np.array(
        [
            [1402.388, 5.03830, -5.81090e-2, 3.3432e-4, -1.47797e-6, 3.1419e-9],
            [0.153563, 6.8999e-4, -8.1829e-6, 1.3632e-7, -6.1260e-10, 0.0],
            [3.1260e-5, -1.7111e-6, 2.5986e-8, -2.5353e-10, 1.0415e-12, 0.0],
            [-9.7729e-9, 3.8513e-10, -2.3654e-12, 0.0, 0.0, 0.0],
        ]
    )

    d00, d10 = 1.727e-3, -7.9836e-6
    x0 = x1 = x2 = x3 = np.zeros(T.size)

    for i in np.arange(5, -1, -1):
        x0 = x0 * T + c[0, i]

    for i in np.arange(4, -1, -1):
        x1 = x1 * T + c[1, i]

    for i in np.arange(4, -1, -1):
        x2 = x2 * T + c[2, i]

    for i in np.arange(2, -1, -1):
        x3 = x3 * T + c[3, i]

    SP /= 10.0
    cw = x0 + (x1 + (x2 + x3 * SP) * SP) * SP
    x0 = x1 = x2 = x3 = np.zeros(T.size)

    for i in np.arange(4, -1, -1):
        x0 = x0 * T + a[0, i]

    for i in np.arange(4, -1, -1):
        x1 = x1 * T + a[1, i]

    for i in np.arange(3, -1, -1):
        x2 = x2 * T + a[2, i]

    for i in np.arange(2, -1, -1):
        x3 = x3 * T + a[3, i]

    atp = x0 + (x1 + (x2 + x3 * SP) * SP) * SP
    btp = b[0, 0] + b[0, 1] * T + (b[1, 0] + b[1, 1] * T) * SP
    dtp = d00 + d10 * SP
    SS: npt.NDArray = cw + atp * S + btp * np.power(S, 3 / 2) + dtp * np.power(S, 2)

    return SS


def _deriveDelGrosso(S: npt.NDArray, T: npt.NDArray, SP: npt.NDArray) -> npt.NDArray:
    SP = SP * 1.019716 / 10.0  # convert dbar to 1000kg/cm^2
    ct = 5.012285 * T - 5.51184e-2 * np.power(T, 2) + 2.21649e-4 * np.power(T, 3)
    cs = 1.329530 * S + 1.288598e-4 * np.power(S, 2)
    cp = 0.1560592 * SP + 2.449993e-5 * np.power(SP, 2) - 8.833959e-9 * np.power(SP, 3)

    cstp = (
        6.353509e-3 * T * SP
        - 4.383615e-7 * np.power(T, 3) * SP
        - 1.593895e-6 * T * np.power(SP, 2)
        + 2.656174e-8 * np.power(T, 2) * np.power(SP, 2)
        + 5.222483e-10 * T * np.power(SP, 3)
        - 1.275936e-2 * S * T
        + 9.688441e-5 * S * np.power(T, 2)
        - 3.406824e-4 * S * T * SP
        + 4.857614e-6 * np.power(S, 2) * T * SP
        - 1.616745e-9 * np.power(S, 2) * np.power(SP, 2)
    )
    SS: npt.NDArray = 1402.392 + ct + cs + cp + cstp

    return SS


def _deriveWilson(S: npt.NDArray, T: npt.NDArray, SP: npt.NDArray) -> npt.NDArray:
    T = T * 1.00024  # convert t90 to t68
    SP = SP / 100.0  # convert dbar to MPa

    ct = (
        4.5721 * T
        - 4.4532e-2 * np.power(T, 2)
        - 2.6045e-4 * np.power(T, 3)
        + 7.9851e-6 * np.power(T, 4)
    )
    cs = (1.39799 - 1.69202e-3 * (S - 35.0)) * (S - 35.0)
    cp = (
        1.63432 * SP
        - 1.06768e-3 * np.power(SP, 2)
        + 3.73403e-6 * np.power(SP, 3)
        - 3.6332e-8 * np.power(SP, 4)
    )

    cstp = (
        -1.1244e-10 * T
        + 7.7711e-7 * np.power(T, 2)
        + 7.85344e-4 * SP
        - 1.3458e-5 * np.power(SP, 2)
        + 3.2203e-7 * SP * T
        + 1.6101e-8 * np.power(T, 2) * SP
    )
    cstp = cstp * (S - 35.0)
    cstp = (
        cstp
        + SP
        * (
            -1.8974e-3 * T
            + 7.6287e-5 * np.power(T, 2)
            + 4.6176e-7 * np.power(T, 3)
            + np.power(SP, 2) * (-2.6301e-5 * T + 1.9302e-7 * np.power(T, 2))
            - 2.0831e-7 * np.power(SP, 3)
        )
        * T
    )
    SS: npt.NDArray = 1449.14 + ct + cs + cp + cstp

    return SS


def derivesoundspeed(self: RSK, soundSpeedAlgorithm: str = "UNESCO") -> None:
    """Calculate the speed of sound.

    Args:
        soundSpeedAlgorithm (str, optional): algorithm to use, with the option of "UNESCO", "DelGrosso", or "Wilson".
            Defaults to "UNESCO".

    Computes the speed of sound using temperature, salinity and pressure data.
    It provides three methods: UNESCO (Chen and Millero), Del Grosso, and Wilson, among which UNESCO is the default.
    The result is added to the :obj:`.RSK.data` field of the current RSK instance, and metadata in :obj:`.RSK.channels` is updated.

    References:
        * C-T. Chen and F.J. Millero, Speed of sound in seawater at high pressures (1977) J. Acoust. Soc. Am. 62(5) pp 1129-1135
        * V.A. Del Grosso, New equation for the speed of sound in natural waters (with comparisons to other equations) (1974) J. Acoust. Soc. Am 56(4) pp 1084-1091
        * W. D. Wilson, Equations for the computation of the speed of sound in sea water, Naval Ordnance Report 6906, US Naval Ordnance Laboratory, White Oak, Maryland, 1962.

    Example:

    >>> rsk.derivesoundspeed()
    ... # Optional arguments
    ... rsk.derivesoundspeed(soundSpeedAlgorithm="DelGrosso")
    """
    self.dataexistsorerror()
    self.channelsexistorerror([Temperature, Salinity, SeaPressure])

    salinity = self.data[Salinity.longName]
    temperature = self.data[Temperature.longName]
    seaPressure = self.data[SeaPressure.longName]

    if soundSpeedAlgorithm == "UNESCO":
        speedOfSound = _deriveUnesco(salinity, temperature, seaPressure)
    elif soundSpeedAlgorithm == "DelGrosso":
        speedOfSound = _deriveDelGrosso(salinity, temperature, seaPressure)
    elif soundSpeedAlgorithm == "Wilson":
        speedOfSound = _deriveWilson(salinity, temperature, seaPressure)
    else:
        raise ValueError(f"Invoked with an unsupported algorithm: {soundSpeedAlgorithm}")

    self.appendchannel(SpeedOfSound, speedOfSound, 0, 1)
    self.appendlog(f"Speed of sound derived using the {soundSpeedAlgorithm} algorithm.")


def deriveA0A(self: RSK) -> None:
    """Apply the RBRquartz³ BPR|zero internal barometer readings to correct for drift in the marine Digiquartz pressure
    readings using the A-zero-A method.

    Uses the A-zero-A technique to correct drift in the Digiquartz® pressure gauge(s). This is done by periodically switching
    the applied pressure that the gauge measures from seawater to the atmospheric conditions inside the housing.
    The drift in quartz sensors is proportional to the full-scale rating, so a reference barometer - with hundreds of times less drift
    than the marine gauge - is used to determine the behaviour of the marine pressure measurements.
    The result is added to the :obj:`.RSK.data` field of the current RSK instance, and metadata in :obj:`.RSK.channels` is updated.

    The A-zero-A technique, as implemented in this method, works as follows. The barometer pressure and the Digiquartz® pressure(s)
    are averaged over the last 30 s of each internal pressure calibration cycle. Using the final 30 s ensures that the transient
    portion observed after the valve switches is not included in the drift calculation. The averaged Digiquartz® pressure(s) are
    subtracted from the averaged barometer pressure, and these values are linearly interpolated onto the original timestamps to
    form the pressure correction. The drift-corrected pressure is the sum of the measured Digiquartz® pressure plus the drift correction.

    .. image:: /img/RSKderiveAOA.png
        :scale: 80%
        :alt: derive AOA diagram

    Example:

    >>> rsk.deriveA0A()
    """
    self.dataexistsorerror()

    bprChannels = [
        c.longName
        for c in self.channels
        if c.shortName == BprPressure.shortName and c.longName in self.data.dtype.names
    ]

    if len(bprChannels) == 0 or not self.channelexists(BarometerPressure):
        raise ValueError("No derived Digiquartz pressure channel found. See RSK.deriveBPR().")

    # Regex to determine whether the current BPR channel has a postfixed number
    hasNumRe = re.compile(r"[\s_]*(\d+)")

    # Extract the valve event timestamps (the start and end of Patm phase)
    # Divide by 1000 to convert from milliseconds to seconds
    tStart = [
        r.tstamp1.astype("float64") / 1000 for r in self.regions if isinstance(r, RegionAtmosphere)
    ]
    tEnd = [
        r.tstamp2.astype("float64") / 1000 for r in self.regions if isinstance(r, RegionAtmosphere)
    ]
    regionCount = len(tStart)

    timestamp = self.data["timestamp"].astype("float64") / 1000
    barPressure = self.data[BarometerPressure.longName]

    for i, bprChannel in enumerate(bprChannels):
        bprPressure = self.data[bprChannel]
        p0 = np.full(regionCount, np.nan)
        p1 = np.full(regionCount, np.nan)
        t30 = np.full(regionCount, np.nan)

        # Get the mean pressure values from the 30 second window
        for j in range(regionCount):
            window = np.flatnonzero(
                np.logical_and(
                    timestamp >= tEnd[j] - 31,
                    timestamp <= tEnd[j] - 1,
                )
            )
            t30[j] = np.min(timestamp[window]) + 15
            p0[j] = np.nanmean(barPressure[window])
            p1[j] = np.nanmean(bprPressure[window])

        # Pressure correction term to be added to measured pressure
        pressureCorrection = interpolate.interp1d(t30, p0 - p1, bounds_error=False)(timestamp)

        for j in range(regionCount):
            window = np.flatnonzero(
                np.logical_and(
                    timestamp >= tStart[j],
                    timestamp <= tEnd[j],
                )
            )
            pressureCorrection[window] = np.nan

        bprCorrection = bprPressure + pressureCorrection

        # Make postfix numbers match if we find one
        if m := hasNumRe.search(bprChannel):
            n = m.group(1)

            self.appendchannel(
                BprCorrectedPressure.withnewname(f"{BprCorrectedPressure.longName}{n}"),
                bprCorrection,
                0,
                1,
            )
            self.appendchannel(
                PressureDrift.withnewname(f"{PressureDrift.longName}{n}"),
                pressureCorrection,
                0,
                1,
            )
        else:
            self.appendchannel(BprCorrectedPressure, bprCorrection, 0, 1)
            self.appendchannel(PressureDrift, pressureCorrection, 0, 1)

        self.appendlog("BPR pressure(s) corrected for drift using barometer readings.")


def _deriveParos(
    accPeriods: npt.NDArray,
    tempPeriods: npt.NDArray,
    tempCoefficients: npt.NDArray,
    accCoefficients: npt.NDArray,
) -> Tuple[npt.NDArray, npt.NDArray]:
    u0 = tempCoefficients[0]

    y1, y2, y3 = tempCoefficients[1], tempCoefficients[2], tempCoefficients[3]

    c1, c2, c3 = accCoefficients[0], accCoefficients[1], accCoefficients[2]
    d1, d2 = accCoefficients[3], accCoefficients[4]
    t1, t2, t3, t4, t5 = (
        accCoefficients[5],
        accCoefficients[6],
        accCoefficients[7],
        accCoefficients[8],
        accCoefficients[9],
    )

    U = np.array((tempPeriods / (1e-6)) - u0)
    temperature = np.array(y1 * U + y2 * U**2 + y3 * U**3)
    Tsquare = (accPeriods / (1e-6)) * (accPeriods / (1e-6))

    C = np.array(c1 + c2 * U + c3 * U**2)
    D = np.array(d1 + d2 * U)
    T0 = np.array(t1 + t2 * U + t3 * U**2 + t4 * U**3 + t5 * U**4)

    acceleration = C * (1 - ((T0 * T0) / Tsquare)) * (1 - D * (1 - ((T0 * T0) / Tsquare)))

    return acceleration, temperature


def _alignParos(
    accX: npt.NDArray, accY: npt.NDArray, accZ: npt.NDArray, alignmentmatrix: Collection[float]
) -> Tuple[npt.NDArray, npt.NDArray, npt.NDArray]:
    # input and output acceleration in m/s^-2
    alignmentmatrix = np.array(alignmentmatrix)
    gx = alignmentmatrix[0, 0] * accX + alignmentmatrix[0, 1] * accY + alignmentmatrix[0, 2] * accZ
    gy = alignmentmatrix[1, 0] * accX + alignmentmatrix[1, 1] * accY + alignmentmatrix[1, 2] * accZ
    gz = alignmentmatrix[2, 0] * accX + alignmentmatrix[2, 1] * accY + alignmentmatrix[2, 2] * accZ

    return gx, gy, gz


def deriveAPT(
    self: RSK,
    Alignment_coefficients: Collection[float] = None,
    Temperature_coefficients: Collection[float] = None,
    Acceleration_coefficients: Collection[float] = None,
) -> None:
    """Convert APT accelerations period and temperature period into accelerations and temperature.

    The RBRquartz³ APT is a combined triaxial quartz accelerometer and a bottom pressure recorder. It is equipped with a Paroscientific, Inc. triaxial accelerometer
    and records the acceleration output frequencies from the accelerometer. Both 'full' and 'EPdesktop' RSK files contain only frequencies for acceleration and temperature.

    This method derives 3-axis accelerations from the accelerometer frequency channels. It implements
    the calibration equations developed by Paroscientific, Inc. to derive accelerations. It requires users
    to input the alignment, temperature and acceleration coefficients. The coefficients are available
    on the Paroscientific, Inc. triax accelerometer instrument configuration sheet, which is shipped along
    with the logger. Derived accelerations and temperature are added to the :obj:`.RSK.data` field of the
    current RSK instance, and the metadata in :obj:`.RSK.channels` is updated.

    .. image:: /img/RSKderiveAPT.png
        :scale: 80%
        :align: center
        :alt: an example of Paroscientific, Inc. triax accelerometer instrument configuration sheet

    Example:

    >>> Alignment_coefficients = [
    ...         [1.00024800955343, -0.00361697821901, -0.01234855907175],
    ...         [-0.00361697821901, 1.0000227853442, -0.00151293870726],
    ...         [-0.01234855907175, 0.00151293870726, 1.00023181988111],
    ...     ]
    ... Temperature_coefficients = [
    ...         [5.795742, 5.795742, 5.795742],
    ...         [-3938.81, -3938.684, -3938.464],
    ...         [-9953.514, -9947.209, -9962.304],
    ...         [0, 0, 0]
    ...     ]
    ... Acceleration_coefficients = [
    ...         [166.34824076, 156.24548496, -163.35657396],
    ...         [-5.328037,    -17.1992,     12.40078],
    ...         [-261.0626,    -342.8823,    215.658],
    ...         [0.03088299,   0.03029925,   0.03331123],
    ...         [0,            0,            0],
    ...         [29.04551984,  29.65519865,  29.19887879],
    ...         [-0.291685,    1.094704,     0.276486],
    ...         [24.50986,     31.78739,     30.48166],
    ...         [0,            0,            0],
    ...         [0,            0,            0],
    ...     ]
    ... rsk.deriveAPT(Alignment_coefficients, Temperature_coefficients, Acceleration_coefficients)
    """
    self.dataexistsorerror()

    if (
        (not (Alignment_coefficients))
        | (not (Temperature_coefficients))
        | (not (Acceleration_coefficients))
    ):
        raise ValueError(
            f"Invalid coefficients. Please insert the correct coefficients from your Paroscientific, Inc. triax accelerometer instrument configuration sheet"
        )

    # Find APT by looking for "SACC" in the partNumber or 7-digit partNumber list for APT
    if self.instrument.partNumber:
        isAPT = "SACC" in self.instrument.partNumber
        isAPT1 = self.instrument.partNumber in ["0004274", "0006501", "0010311"]
        isAPT = isAPT | isAPT1
    else:
        raise ValueError(
            f"No part number is included in the file. Please upgrade your RSK file version to at least v2.10.0."
        )

    # Find the 4 APT channels (3 * peri00 + 1 * peri01)
    if isAPT:
        if len(self.channels) < 4:
            raise ValueError(
                f"RBRquartzAPT should contain at least 4 channels. Please apply RSK.deriveAPT to RSK files with triax accelerometer measurements."
            )
        else:
            for i, channel in enumerate(self.channels):
                if i > len(self.channels) - 4:
                    raise ValueError(f"No 3-axis acceleration period measurements detected.")
                if (
                    channel.shortName == "peri00"
                    and self.channels[i + 1].shortName == "peri00"
                    and self.channels[i + 2].shortName == "peri00"
                    and self.channels[i + 3].shortName == "peri01"
                ):
                    APTchannelx = channel.longName
                    APTchannely = self.channels[i + 1].longName
                    APTchannelz = self.channels[i + 2].longName
                    APTchanneltemp = self.channels[i + 3].longName
                    break
    else:
        raise ValueError(
            f"No RBRquartzAPT detected. Please apply RSK.deriveAPT to RSK files with triax accelerometer measurements."
        )

    accX, tempX = _deriveParos(
        accPeriods=self.data[APTchannelx] * 1e-12,
        tempPeriods=self.data[APTchanneltemp] * 1e-12,
        tempCoefficients=np.array(Temperature_coefficients)[:, 0],
        accCoefficients=np.array(Acceleration_coefficients)[:, 0],
    )
    accY, tempY = _deriveParos(
        accPeriods=self.data[APTchannely] * 1e-12,
        tempPeriods=self.data[APTchanneltemp] * 1e-12,
        tempCoefficients=np.array(Temperature_coefficients)[:, 1],
        accCoefficients=np.array(Acceleration_coefficients)[:, 1],
    )
    accZ, tempZ = _deriveParos(
        accPeriods=self.data[APTchannelz] * 1e-12,
        tempPeriods=self.data[APTchanneltemp] * 1e-12,
        tempCoefficients=np.array(Temperature_coefficients)[:, 2],
        accCoefficients=np.array(Acceleration_coefficients)[:, 2],
    )

    accX, accY, accZ = _alignParos(accX, accY, accZ, Alignment_coefficients)
    temp = (tempX + tempY + tempZ) / 3

    self.appendchannel(AccelerationX, accX, 0, 1)
    self.appendchannel(AccelerationY, accY, 0, 1)
    self.appendchannel(AccelerationZ, accZ, 0, 1)
    self.appendchannel(AccelerometerTemperature, temp, 0, 1)

    self.appendlog("APT accelerations and temperature derived from period data.")
