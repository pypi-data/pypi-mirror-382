#!/usr/bin/env python3
# Standard/external imports
from __future__ import annotations
from typing import *
import numpy as np
import numpy.ma as ma
import numpy.typing as npt
import re
from scipy import interpolate, signal


def semver2int(semver: str) -> int:
    """Take a semantic version string and turn it into an integer
    that can be compared using logical operators (e.g., <, ==, >).

    Args:
        semver (str): the semantic verison string to convert.

    Returns:
        int: the converted version string.

    Example:

    >>> semver2int("1.0.0") # = 1000000
    ... semver2int("1.20.2") # = 1020002
    """
    semverStr: str = ""

    components = semver.split(".")
    components += ["0"] * (3 - len(components))
    for c in components:
        semverStr += c.zfill(3)

    return int(semverStr)


def formatchannelname(unformattedChannelName: str) -> str:
    """Take a given channel name and return a formatted version
    adhering to the standard used by pyRSKtools.

    Args:
        unformattedChannelName (str): the unformatted channel.

    Returns:
        str: the input channel formatted.

    Example:

    >>> formatchannelname("Conductivity") # = "conductivity"
    ... formatchannelname("Dissolved O₂ saturation") # = "dissolved_o2_saturation"
    ... formatchannelname("1/10 wave height") # = "one_tenth_wave_height"
    """
    formatted = (
        unformattedChannelName.lower()
        .strip()
        .replace(" ", "_")
        .replace("1/10", "one_tenth")
        .replace("₂", "2")
    )
    formatted = re.sub(r"[^ -~]", "_", formatted)  # Replace any non-ascii values with '_'

    if len(formatted) > 0 and formatted[0].isnumeric():
        formatted = f"x{formatted}"

    return formatted


def createuniquechannelname(
    unformattedChannelName: str, existingChannelNames: Collection[str]
) -> str:
    """Format the given channel name using :meth:`.formatchannelname` and, if needed, alter it further
    to make sure it is unique against the list of existing channel names.

    This method is most useful when you already have an established
    list of channel names (e.g., :obj:`RSK.channelNames`) and want to append
    an additional channel.

    Args:
        unformattedChannelName (str): the channel to format.
        existingChannelNames (Collection[str]): a list of already existing channels.

    Returns:
        str: the original channel name but properly formatted/unique.

    The example below outputs ``"conductivity1"`` if the channel exists in ``rsk.channelNames``,
    or ``"conductivity"`` if the channel does not exist in the list.

    Example:

    >>> createuniquechannelname("Conductivity", rsk.channelNames)
    """
    channelName = formatchannelname(unformattedChannelName)

    count = 0  # Duplicate channel name count
    for existingChannel in existingChannelNames:
        if existingChannel.startswith(channelName):
            count += 1

    return channelName if count <= 0 else f"{channelName}{count}"


def rsktime2datetime(rsktime: int) -> np.datetime64:
    """Converts milliseconds (e.g., a timestamp from a .rsk file)
    into a NumPY ``datetime64`` object with millisecond precision.

    Args:
        rsktime (int): RSK time/milliseconds to convert.

    Returns:
        np.datetime64: the resultant ``datetime64`` object.
    """
    datetime = np.datetime64(rsktime, "ms")
    return datetime


def datetime2rsktime(datetime: np.datetime64) -> int:
    """Converts a NumPY ``datetime64`` object (of any precision)
    into milliseconds (integer value).

    Args:
        datetime (np.datetime64): the ``datetime64`` object to convert.

    Returns:
        int: the resultant milliseconds integer.
    """
    datetime = np.datetime64(datetime, "ms")  # Make sure in "ms"
    rsktime: int = int(datetime.astype(np.uint64))
    return rsktime


def intoarray(data: Any, dtype: str = "float64") -> npt.NDArray:
    """Tries to transform any given value into a 1-D NumPY array
    with the specified data type.

    Args:
        data (Any): the data to try and convert (e.g., the value of type int, list, iterable, etc)
        dtype (str): the data type of the created NumPY array (any valid NumPY type). Defaults to "float64".

    Raises:
        ValueError: if the given value could not be transformed into a NumPY array.

    Returns:
        npt.NDArray: the 1-D NumPY array containing the passed-in values.

    Example:

    >>> intoarray(1)
    ... intoarray([1, 2, 3])
    ... intoarray(range(3))
    """
    if isinstance(data, np.ndarray):
        return data

    try:
        if hasattr(data, "__size__"):
            return np.array(data, dtype=dtype)
        elif hasattr(data, "__iter__"):
            return np.fromiter(data, dtype=dtype)
        else:
            return np.array([data], dtype=dtype)
    except Exception:
        pass

    raise ValueError(f"Could not convert data into a {dtype} array.")


def mirrorpad(a: npt.NDArray, padSize: int) -> npt.NDArray:
    # Although the code below will work with a padSize greater than the array length,
    # the array will only be padded to a max of the array length on each side.
    # To avoid unexpected behaviour, throw on error when padSize is too big.
    if padSize > a.size:
        raise ValueError(
            f"Argument 'padSize' with value {padSize} is greater than given array length of {a.size}"
        )

    pre = a[:padSize][::-1]
    post = a[-padSize:][::-1]
    return np.concatenate((pre, a, post))


def nanpad(a: npt.NDArray, padSize: int) -> npt.NDArray:
    if padSize > a.size:
        raise ValueError(
            f"Argument 'padSize' with value {padSize} is greater than given array length of {a.size}"
        )

    pad = np.full(padSize, np.nan)
    return np.concatenate((pad, a, pad))


def zeroorderholdpad(a: npt.NDArray, padSize: int) -> npt.NDArray:
    if padSize > a.size:
        raise ValueError(
            f"Argument 'padSize' with value {padSize} is greater than given array length of {a.size}"
        )

    pre = np.full(padSize, a[0])
    post = np.full(padSize, a[-1])
    return np.concatenate((pre, a, post))


def padseries(a: npt.NDArray, padSize: int, edgePad: str) -> npt.NDArray:
    if edgePad == "mirror":
        return mirrorpad(a, padSize)
    elif edgePad == "nan":
        return nanpad(a, padSize)
    elif edgePad == "zeroorderhold":
        return zeroorderholdpad(a, padSize)
    else:
        raise ValueError(
            f"Argument 'edgePad' ({edgePad}) is not recognized. Must be 'mirror', 'nan' or 'zeroorderhold'."
        )


def runavg(a: npt.NDArray, windowLength: int, edgePad: str = "mirror") -> npt.NDArray:
    if windowLength % 2 == 0:
        raise ValueError(f"Given argument 'windowLength' ({windowLength}) must be odd: ")

    padSize = (windowLength - 1) // 2
    padded = padseries(a, padSize, edgePad)
    padded = np.array(padded, dtype=float)

    return np.fromiter(
        (
            np.nanmean(padded[i : i + windowLength])
            if np.flatnonzero(np.isfinite(padded[i : i + windowLength])).size > 0
            else np.nan
            for i in range(a.size)
        ),
        "float64",
    )


def runmed(a: npt.NDArray, windowLength: int, edgePad: str = "mirror") -> npt.NDArray:
    if windowLength % 2 == 0:
        raise ValueError(f"Given argument 'windowLength' ({windowLength}) must be odd: ")

    padSize = (windowLength - 1) // 2
    padded = padseries(a, padSize, edgePad)
    padded = np.array(padded, dtype=float)

    return np.fromiter(
        (
            np.nanmedian(padded[i : i + windowLength])
            if np.flatnonzero(np.isfinite(padded[i : i + windowLength])).size > 0
            else np.nan
            for i in range(a.size)
        ),
        "float64",
    )


def runtriang(a: npt.NDArray, windowLength: int, edgePad: str = "mirror") -> npt.NDArray:
    coeff = np.zeros(windowLength, dtype=np.float64)
    if windowLength % 2 == 0:
        raise ValueError(f"Given argument 'windowLength' ({windowLength}) must be odd: ")

    for i in range(windowLength):
        if i <= windowLength // 2:
            coeff[i] = 2 * (i + 1) / (windowLength + 1)
        else:
            coeff[i] = 2 - (2 * (i + 1) / (windowLength + 1))

    normcoeff = coeff / np.sum(coeff)
    padSize = (windowLength - 1) // 2
    padded = padseries(a, padSize, edgePad)
    padded = np.array(padded, dtype=float)

    return np.fromiter(
        (
            np.nansum(padded[i : i + windowLength] * np.round(normcoeff, decimals=15))
            if np.flatnonzero(np.isfinite(padded[i : i + windowLength])).size > 0
            else np.nan
            for i in range(a.size)
        ),
        "float64",
    )


def calculatevelocity(depth: npt.NDArray, time: npt.NDArray) -> npt.NDArray:
    """Calculates velocity using the midpoints of depth and time and
    interpolates back to the original time and depth point given.

    Args:
        depth (npt.NDArray): Depth values in m.
        time (npt.NDArray): Time at each depth value.

    Returns:
        npt.NDArray: velocity at the input time values in m/s.
    """
    seconds = time.astype("float64") / 1000.0  # Convert from ms to seconds
    deltaD = np.diff(depth)
    deltaT = np.diff(seconds)
    dDdT = deltaD / deltaT
    midtime = seconds[:-1] + deltaT / 2.0

    velocity: npt.NDArray = interpolate.interp1d(
        midtime,
        dDdT,
        kind="linear",
        fill_value="extrapolate",
    )(seconds)

    return velocity


def lagave(inArray: npt.NDArray) -> npt.NDArray:
    """Mimics Matlab's tsmovavg(in, 's', 2).

    References:
        * https://www.mathworks.com/help/finance/tsmovavg.html
    """
    outArray = np.full(inArray.size, np.nan)
    lag = 2
    tmp = signal.lfilter(np.ones(lag) / lag, 1, inArray)
    outArray[lag - 1 :] = tmp[lag - 1 :]
    return outArray


def getcastdirection(inPressure: npt.NDArray, direction: str) -> bool:
    def isUpcast(inPressure: npt.NDArray) -> bool:
        # Returns true if pressure decreases, false if pressure increases
        if inPressure[0] > inPressure[-1]:
            isup = True
        else:
            isup = False
        return isup

    def isDowncast(inPressure: npt.NDArray) -> bool:
        # Returns true if pressure decreases, false if pressure increases
        if inPressure[0] < inPressure[-1]:
            isdown = True
        else:
            isdown = False
        return isdown

    if isUpcast(inPressure) and (direction.lower() == "up"):
        castdir = True
    elif isDowncast(inPressure) and (direction.lower() == "down"):
        castdir = True
    else:
        castdir = False

    return castdir


def shiftarray(inArray: npt.NDArray, shift: int, edgePad: str = "mirror") -> npt.NDArray:
    """Shift a time series by a specified number of samples.

    Args:
        inArray (npt.NDArray): input time series.
        shift (int): number of samples to shift by.
        edgePad (str, optional): Values to set the beginning or end values. Options are
            "mirror", "zeroorderhold", "nan", or "union". Defaults to "mirror".

    Returns:
        npt.NDArray: the shifted time series.

    Shifts a time series by a lag corresponding to an integer
    number of samples. Negative shifts correspond to moving the samples
    backward in time (earlier), positive to forward in time
    (later). Values at either the beginning or the end are set to a
    value specified by the argument "edgepad" to conserve the length of
    the input vector, except for the particular case of 'union'.
    """
    if edgePad == "mirror":
        inPad = mirrorpad(inArray, abs(shift))
    elif edgePad == "zeroorderhold":
        inPad = zeroorderholdpad(inArray, abs(shift))
    elif edgePad == "nan":
        inPad = nanpad(inArray, abs(shift))
    elif edgePad == "union":
        inPad = nanpad(inArray, abs(shift))
    else:
        raise ValueError(f"Unrecognized value for argument 'edgepad': {edgePad}")

    Ilag = np.arange(inArray.size)
    if shift <= 0:
        Ilag -= 2 * shift

    out: npt.NDArray = inPad[Ilag]
    if edgePad == "union":
        out = out[~np.isnan(out)]

    return out
